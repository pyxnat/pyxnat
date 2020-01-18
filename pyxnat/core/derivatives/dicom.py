XNAT_RESOURCE_NAME = 'DICOM'

def scandate(self):
    import os.path as op
    import os
    import tempfile
    import pydicom
    from datetime import datetime

    f = list(self.files())[0]

    fp = op.join(tempfile.gettempdir(), 'test.dcm')
    _, fp = tempfile.mkstemp(suffix='.dcm')
    f.get(dest=fp)
    d = pydicom.read_file(fp)

    if hasattr(d, 'AcquisitionDate'):
        acquisition_date = d.AcquisitionDate
    else:
        acquisition_date = d.AcquisitionDateTime[:8]

    os.remove(fp)
    ad = datetime.strptime(acquisition_date, '%Y%m%d').strftime('%m-%d-%Y')
    return ad
