XNAT_RESOURCE_NAME = 'SPM12_SEGMENT'

def volumes(self):
        import tempfile
        import nibabel as nib
        import numpy as np

        vols = []
        _, fp = tempfile.mkstemp(suffix='.nii.gz')

        names = ['c1', 'c2', 'c3']
        for kls in names:
            f = [each for each in self.files() if each.id().startswith(kls)][0]
            f.get(fp)
            d = nib.load(fp)
            size = np.prod(d.header['pixdim'].tolist()[:4])
            v = np.sum(d.dataobj) * size
            vols.append((kls, v))

        return dict(vols)
