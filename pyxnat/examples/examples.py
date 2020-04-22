import os
from subprocess import Popen
from multiprocessing import Pool

import pyxnat

url = 'https://imagen.cea.fr/imagen_database'

login = ''
password = ''
interface = pyxnat.Interface(url, login, password)

def bet(in_image):
    path, name = os.path.split(in_image)
    in_image = os.path.join(path, name.rsplit('.')[0])
    out_image = os.path.join(path, name.rsplit('.')[0] + '_brain')

    print('==> %s' % in_image[-120:])

    Popen('bet2 %s %s -f 0.5 -g 0 ' % (in_image, out_image),
          shell=True).communicate()

    return out_image

def notify(message):
    print('<== %s' % message[-120:])

pool = Pool(processes=8)

for mprage in interface.select(
    '//experiments/*SessionA*/assessors/*ADNI*/out/resources/files'
    ).where([('psytool:tci_parentData/TCI051', '=', '1'), 'AND']):

    pool.apply_async(bet, (mprage.get(),), callback=notify)

pool.close()
pool.join()
