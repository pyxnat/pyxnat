XNAT_RESOURCE_NAME = 'BAMOS'


def volume(self):
    import os
    import nibabel as nib
    import tempfile
    import numpy as np

    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    f = list(self.files('CorrectLesion_*nii.gz'))[0]
    f.get(fp)
    d = nib.load(fp)
    size = np.prod(d.header['pixdim'].tolist()[:4])
    v = np.sum(d.dataobj) * size
    return v
