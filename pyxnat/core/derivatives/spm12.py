XNAT_RESOURCE_NAMES = ['SPM12_SEGMENT', 'SPM12_SEGMENT_T1T2']


def volumes(self):
    import os
    import tempfile
    import nibabel as nib
    import numpy as np

    vols = []
    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    names = ['c1', 'c2', 'c3']
    for kls in names:
        f = [each for each in self.files() if each.id().startswith(kls)][0]
        f.get(fp)
        d = nib.load(fp)
        size = np.prod(d.header['pixdim'].tolist()[:4])
        v = np.sum(d.dataobj) * size
        vols.append((kls, v))

    os.remove(fp)
    return dict(vols)


def download_rc(self, path):
    '''Downloads a local copy of DARTEL imports.'''
    import os.path as op
    rc_files = ['rc1', 'rc2']
    for each in rc_files:
        res = self._intf.array.experiments(experiment_id=self.parent().id(),
                                           columns=['subject_label']).data[0]
        subject_label = res['subject_label']
        id = res['ID']
        fp = '%s_%s_%s.nii.gz' % (each[-3:], subject_label, id)
        list(self.files('%s*' % each))[0].get(op.join(path, fp))
