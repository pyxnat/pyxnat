import os
from subprocess import Popen
import multiprocessing as mp

import pyxnat

URL = 'https://central.xnat.org' # central URL
BET = 'fsl4.1-bet2'              # BET executable path

central = pyxnat.Interface(URL, anonymous=True) # connection object

def bet(in_img, in_hdr): # Python wrapper on FSL BET, essentially a system call
    in_image = in_img.get()     # download .img
    in_hdr.get()                # download .hdr
    path, name = os.path.split(in_image)
    in_image = os.path.join(path, name.rsplit('.')[0])
    out_image = os.path.join(path, name.rsplit('.')[0] + '_brain')
    print('==> %s' % in_image[-120:])
    Popen('%s %s %s' % (BET, in_image, out_image),
          shell=True).communicate()
    return out_image

def notify(message): # message to notify the end of a BET process
    print('<== %s' % message[-120:])

pool = mp.Pool(processes=mp.cpu_count() * 2) # pool of concurrent workers
images = {}
query = ('/projects/CENTRAL_OASIS_CS/subjects/*'
          '/experiments/*_MR1/scans/mpr-1*/resources/*/files/*')
filter_ = [('xnat:mrSessionData/AGE', '>', '80'), 'AND']

for f in central.select(query).where(filter_):
    label = f.label()
    # images are stored in pairs of files (.img, .hdr) in this project
    if label.endswith('.img'):
        images.setdefault(label.split('.')[0], []).append(f)
    if f.label().endswith('.hdr'):
        images.setdefault(label.split('.')[0], []).append(f)
    # download and process both occur in parallel within the workers
    for name in images.keys():
        if len(images[name]) == 2: # if .img and .hdr XNAT references are ready
            img, hdr = images.pop(name)                        # get references
            pool.apply_async(bet, (img, hdr), callback=notify) # start worker
pool.close()
pool.join()
