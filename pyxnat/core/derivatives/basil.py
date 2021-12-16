XNAT_RESOURCE_NAMES = ['BASIL']


def volumes(self):
    """Partial volume segmentations for CSF, GM, WM (fsl_anat)"""
    import os
    import tempfile
    import nibabel as nib
    import numpy as np

    vols = []
    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    names = ['T1_fast_pve_0', 'T1_fast_pve_1', 'T1_fast_pve_2']
    for kls in names:
        f = self.files('*{}*'.format(kls))[0]
        f.get(fp)
        d = nib.load(fp)
        size = np.prod(d.header['pixdim'].tolist()[:4])
        v = np.sum(d.dataobj) * size
        vols.append((kls, v))

    os.remove(fp)
    return dict(vols)


def perfusion(self):
    """Perfusion and arrival-time mean values"""
    import pandas as pd

    def _fix_label(label):
        """Some BASIL mean files have typos in their names. This helper
        fixes them so they are consistent with the metric represented."""

        d = {'arrival_wm_wm_mean': 'arrival_wm_mean',
             'perfusion_wm_wm_mean': 'perfusion_wm_mean',
             'perfusion_wm_calib_wm_mean': 'perfusion_calib_wm_mean'}

        return d.get(label, label)

    data = []

    mean_files = [f for f in list(self.files('native_space/*.txt'))]
    for f in mean_files:
        fp = f.attributes()['path']
        key = _fix_label(f.attributes()['Name'].split('.txt')[0])
        pvcorr = ('pvcorr' in fp)
        value = float(self._intf.get(f.attributes()['URI']).text.strip())

        data.append([key, pvcorr, value, fp])

    return pd.DataFrame(data, columns=['metric', 'pvcorr', 'value', 'filepath'])


def stats(self):
    """Summary statistics for the perfusion values within each region
    in the Harvard-Oxford cortical and subcortical atlases"""
    import csv
    import pandas as pd
    import os.path as op

    region_stats = []

    stats_files = {'whole_brain': 'region_analysis.csv',
                   'GM': 'region_analysis_gm.csv',
                   'WM': 'region_analysis_wm.csv'}
    for roi, fn in stats_files.items():
        f = self.files('*{}'.format(fn))[0]
        content = self._intf.get(f.attributes()['URI']).text.splitlines()
        for idx, ln in enumerate(csv.reader(content)):
            if idx == 0:
                cols = ['ROI'] + ln
            elif idx > 0:
                region_stats.append([roi] + ln)

    df = pd.DataFrame(region_stats, columns=cols)
    num_cols = ['Nvoxels', 'Mean', 'Std', 'Median',
                'IQR', 'Precision-weighted mean', 'I2']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col])
    return df
