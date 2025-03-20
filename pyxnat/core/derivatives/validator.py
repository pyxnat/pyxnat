XNAT_RESOURCE_NAMES = ['BBRC_VALIDATOR']


def tests(self, name, key=None):
    """
    Looks up a validation test based on the validator name and returns its
    result. If no test name is provided, then a dictionary is returned with
    all the tests from the validation report.

    Args:
        name (String): Root found in the name of the report
            (ex: FreeSurferValidator)
        key (String): Name of the test.
    Returns:
        A `pyxnat` File of the report.

    """
    import json
    j = [e for e in list(self.files('{}*.json'.format(name)))][0]
    j = json.loads(self._intf.get(j._uri).text)
    if key is None:
        return j
    else:
        return j[key]


def pdf(self, name):
    """
    Returns a validator report based on its name. Raises exception if
    multiple reports are found.

    Args:
        name (String): Root found in the name of the report
            (ex: FreeSurferValidator)
    Returns:
        A `pyxnat` File of the report.

    """
    files = list(self.files())
    pdf_file = {each._uri.split('/')[-1]: each for each in files
                if name in each._uri.split('/')[-1] and
                each._uri.split('/')[-1].endswith('.pdf')}

    if len(pdf_file.items()) == 0:
        raise Exception('No %s found' % name)

    keys = list(pdf_file.keys())
    if len(keys) != 1:
        raise Exception('Multiple matching reports found (%s)' % keys)

    f = pdf_file[list(pdf_file.keys())[0]]
    return f


def download_snapshot(self, name, fp):
    """
    Extract snapshot(s) from a validation report given its name.

    Args:
        name (String): Root found in the name of the report
            (ex: FreeSurferValidator)
        fp (String): Path to the file where the snapshot(s) will be saved.
    """

    import os
    import os.path as op
    import tempfile
    from shutil import move

    def extract_snapshots(fp):
        import fitz
        doc = fitz.open(fp)
        dn = op.dirname(fp)
        bn = op.splitext(op.basename(fp))[0]
        images = []
        xrefs = []
        for page in range(len(doc)):
            xrefs.extend([img[0] for img in doc.get_page_images(page)])
        xrefs = sorted(set(xrefs))
        for k, xref in enumerate(xrefs[1:]):
            pix = fitz.Pixmap(doc, xref)
            fp_snap = op.join(dn, "{}_{}.png".format(bn, k))
            if pix.n >= 5:    # CMYK: convert to RGB first
                pix = fitz.Pixmap(fitz.csRGB, pix)
            pix.save(fp_snap)
            images.append(fp_snap)
        return images

    pdf_file = self.pdf(name)

    f, fp1 = tempfile.mkstemp(suffix='.pdf')
    os.close(f)
    pdf_file.get(dest=fp1)

    snaps = extract_snapshots(fp1)

    if len(snaps) == 0:
        raise Exception('No snapshot found in report. %s %s' % (name, fp1))

    files = []  # Will store the snapshots in their final folder
    for i, each in enumerate(snaps):
        bn, _ = op.splitext(fp)
        _, ext = op.splitext(each)
        interm = ''
        if len(snaps) > 1:  # if multiple snapshots then add # in filename
            interm = '_%s' % i
        fp2 = '%s%s%s' % (bn, interm, ext)  # create destination filepath
        move(each, fp2)
        files.append(fp2)

    os.remove(fp1)
    return files
