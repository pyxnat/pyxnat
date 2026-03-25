from .basil import volumes as vols

XNAT_RESOURCE_NAMES = ['FSL_ANAT']


def volumes(self):
    """Partial volume segmentations for CSF, GM, WM (fsl_anat)"""
    return vols(self)


def subcortical_volumes(self):
    """Subcortical volume segmentations"""
    import os
    import tempfile
    import nibabel as nib
    import numpy as np
    import pandas as pd

    labels = {'L_Thal': 10,
              'L_Caud': 11,
              'L_Puta': 12,
              'L_Pall': 13,
              'BrStem': 16,
              'L_Hipp': 17,
              'L_Amyg': 18,
              'L_Accu': 26,
              'R_Thal': 49,
              'R_Caud': 50,
              'R_Puta': 51,
              'R_Pall': 52,
              'R_Hipp': 53,
              'R_Amyg': 54,
              'R_Accu': 58}

    rows = []
    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    f = self.files('*T1_subcort_seg.nii.gz')[0]
    try:
        f.get(fp)
        img = nib.load(fp)
        data = np.asarray(img.dataobj)
        voxel_size = np.prod(img.header['pixdim'].tolist()[:4])

        for roi, label in labels.items():
            volume = np.count_nonzero(data == label) * voxel_size
            rows.append({'region': roi, 'volume': volume})
    finally:
        if os.path.exists(fp):
            os.remove(fp)

    return pd.DataFrame(rows)
