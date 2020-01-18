XNAT_RESOURCE_NAME = 'CAT12_SEGMENT'

def volumes(self):
        import tempfile
        import nibabel as nib
        import numpy as np

        vols = []
        _, fp = tempfile.mkstemp(suffix='.nii.gz')

        names = ['mri/p1', 'mri/p2', 'mri/p3']
        for kls in names:
            f = [each for each in self.files() if each.id().startswith(kls)][0]
            f.get(fp)
            d = nib.load(fp)
            size = np.prod(d.header['pixdim'].tolist()[:4])
            v = np.sum(d.dataobj) * size
            vols.append((kls, v))

        return dict(vols)

def download_rc(self, path):
    '''Downloads a local copy of DARTEL imports. (Keep in mind that in CAT12
    images are named rp*, not rc*.'''
    import os.path as op
    rc_files = ['mri/rp1', 'mri/rp2']
    for each in rc_files:
        res = self._intf.array.experiments(experiment_id=self.parent().id(),
            columns=['subject_label']).data[0]
        subject_label = res['subject_label']
        id = res['ID']
        fp = '%s_%s_%s.nii.gz'%(each[-3:], subject_label, id)
        list(self.files('%s*'%each))[0].get(op.join(path, fp))
