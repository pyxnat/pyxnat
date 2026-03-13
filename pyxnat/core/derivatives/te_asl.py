from . import basil

XNAT_RESOURCE_NAMES = ['TE_ASL']


def perfusion(self):
    """Perfusion and arrival-time mean values"""
    return basil.perfusion(self)


def stats(self):
    """Summary statistics for the perfusion values within each region
    in the Harvard-Oxford cortical and subcortical atlases"""
    import csv
    import pandas as pd
    import os.path as op

    region_stats = []

    stats_files = {'whole_brain_perfusion': 'region_analysis.csv',
                   'GM_perfusion': 'region_analysis_gm.csv',
                   'WM_perfusion': 'region_analysis_wm.csv',
                   'whole_brain_arrival': 'region_analysis_arrival.csv',
                   'GM_arrival': 'region_analysis_arrival_gm.csv',
                   'WM_arrival': 'region_analysis_arrival_wm.csv'}
    for roi, fn in stats_files.items():
        f = self.files('*{}'.format(fn))[0]
        content = self._intf.get(f.attributes()['URI']).text.splitlines()
        for idx, ln in enumerate(csv.reader(content)):
            if idx == 0:
                cols = ['region_analysis'] + ln
            elif idx > 0:
                region_stats.append([roi] + ln)

    df = pd.DataFrame(region_stats, columns=cols)
    num_cols = ['Nvoxels', 'Mean', 'Std', 'Median',
                'IQR', 'Precision-weighted mean', 'I2']
    for col in num_cols:
        df[col] = pd.to_numeric(df[col])
    return df