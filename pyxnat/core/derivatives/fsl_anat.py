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

    vols = []
    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    f = self.files('*T1_subcort_seg.nii.gz')[0]
    f.get(fp)

    nii_img = nib.load(fp)
    data = np.array(nii_img.dataobj)
    size = np.prod(nii_img.header['pixdim'].tolist()[:4])

    for roi in labels.keys():
        label = labels[roi]
        v = np.count_nonzero(data == label) * size
        vols.append({'region': roi,
                     'volume': v})

    os.remove(fp)
    return pd.DataFrame(vols)