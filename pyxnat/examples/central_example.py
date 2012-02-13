import os
from subprocess import Popen
import multiprocessing as mp

import pyxnat


URL = 'https://central.xnat.org'
BET = 'fsl4.1-bet2'

central = pyxnat.Interface(URL)

def bet(in_img, in_hdr):
    in_image = in_img.get()
    in_hdr.get()

    path, name = os.path.split(in_image)
    in_image = os.path.join(path, name.rsplit('.')[0])
    out_image = os.path.join(path, name.rsplit('.')[0] + '_brain')

    print '==> %s' % in_image[-120:]

    Popen('%s %s %s' % (BET, in_image, out_image), 
          shell=True).communicate()

    return out_image

def notify(message):
    print '<== %s' % message[-120:]

pool = mp.Pool(processes=mp.cpu_count() * 2)

_query = ('/projects/CENTRAL_OASIS_CS/subjects/*'
          '/experiments/*_MR1/scans/mpr-1*/resources/*/files/*')

_filter = [('xnat:mrSessionData/AGE', '>', '80'), 'AND']

images = {}

for f in central.select(_query).where(_filter):
    label = f.label()

    if label.endswith('.img'):
        images.setdefault(label.split('.')[0], []).append(f)

    if f.label().endswith('.hdr'):
        images.setdefault(label.split('.')[0], []).append(f)

    for name in images.keys():
        if len(images[name]) == 2:
            img, hdr = images.pop(name)
            pool.apply_async(bet, (img, hdr), callback=notify)

pool.close()
pool.join()
