XNAT_RESOURCE_NAMES = ['TOPUP_DTIFIT', 'DTIFIT', 'DWI_PREPROCESSING']


def download_maps(self, path):
    '''Downloads a local copy of DWI maps (MD, FA, L1 ~axial, RD)'''
    import os.path as op
    rc_files = ['MD', 'FA', 'L1', 'RD']
    for each in rc_files:
        res = self._intf.array.experiments(experiment_id=self.parent().id(),
                                           columns=['subject_label']).data[0]
        subject_label = res['subject_label']
        fp = '%s_%s_%s.nii.gz' % (subject_label, res['ID'], each)
        list(self.files('*%s.nii.gz' % each))[0].get(op.join(path, fp))
