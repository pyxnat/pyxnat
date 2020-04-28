XNAT_RESOURCE_NAMES = ['BBRC_VALIDATOR']

def tests(self, name, key=None):
    import json
    j = [e for e in list(self.files('{}*.json'.format(name)))][0]
    j = json.loads(self._intf.get(j._uri).text)
    if key is None:
        return j
    else:
        return j[key]

def pdf(self, name):
    import logging as log
    files = list(self.files())
    pdf = {each._uri.split('/')[-1]:each for each in files \
        if name in each._uri.split('/')[-1] and \
        each._uri.split('/')[-1].endswith('.pdf')}

    if len(pdf.items()) == 0:
        raise Exception('No %s found'%name)

    keys = list(pdf.keys())
    if len(keys) != 1:
        raise Exception('Multiple matching reports found (%s)'%keys)

    f = pdf[list(pdf.keys())[0]]
    return f

def download_snapshot(self, name, fp):
    import os.path as op
    import shutil
    import os
    import os.path as op
    import tempfile
    import logging as log
    from glob import glob

    def extract_file(fp):
        dn = op.dirname(fp)

        with open(fp, "rb") as file:
            pdf = file.read()

        startmark = b"\xff\xd8"
        startfix = 0
        endmark = b"\xff\xd9"
        endfix = 2
        i = 0

        njpg = 0
        jpeg = []
        while True:
            istream = pdf.find(b"stream", i)
            if istream < 0:
                break
            istart = pdf.find(startmark, istream, istream + 20)
            if istart < 0:
                i = istream + 20
                continue
            iend = pdf.find(b"endstream", istart)
            if iend < 0:
                raise Exception("Didn't find end of stream!")
            iend = pdf.find(endmark, iend - 20)
            if iend < 0:
                raise Exception("Didn't find end of JPG!")

            istart += startfix
            iend += endfix
            jpg = pdf[istart:iend]

            fp = op.join(dn, "jpg%d.jpg" % njpg)
            jpeg.append(fp)
            with open(fp, "wb") as jpgfile:
                jpgfile.write(jpg)

            njpg += 1
            i = iend
        return jpeg

    pdf = self.pdf(name)

    f, fp1 = tempfile.mkstemp(suffix='.pdf')
    os.close(f)
    log.debug('Saving it in %s.'%fp1)
    pdf.get(dest=fp1)

    jpeg = extract_file(fp1)

    if len(glob(op.join(op.dirname(fp1), '*.jpg'))) == 0:
        raise Exception('No snapshot found in report. %s %s'%(name, fp1))

    f, fp2 = tempfile.mkstemp(suffix='.jpg')
    os.close(f) # we dont need the handle
    cmd = 'montage %s/jpg*jpg -background black -geometry 2600x+0+0 '\
        '-tile 1x %s'%(op.dirname(fp1), fp2)
    os.system(cmd)

    cmd = 'mv %s %s'%(fp2, fp)
    os.system(cmd)
    for each in jpeg:
        cmd = 'rm %s'%each
        os.system(cmd)
    cmd = 'rm %s'%fp1
    os.system(cmd)
