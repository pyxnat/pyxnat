import pyxnat
interface = pyxnat.Interface('https://imagen.cea.fr/imagen_database',
                             'login', 'password')

def bet(in_image):
    route, name = os.path.split(in_image)
    in_image = os.path.join(route, name.rsplit('.')[0])
    out_image = os.path.join(route, name.rsplit('.')[0]+'_brain')

    print '==> %s'%in_image[-120:]

    Popen('bet2 %s %s -f 0.5 -g 0 '%(in_image, out_image), shell=True).communicate()

    return out_image

def bet2(url):
    file_object = restcall(url)
    print file_object
    return bet(file_object.rest.get_copy())

def notify(message):
    print '<== %s'%message[-120:]

pool = Pool(processes=8)
start = time.time()

for adni_mprage in interface.select('//experiments/*SessionA*/assessors/*ADNI*/out/resources/files'
                           ).where('psytool:tci_parentData/TCI051 = 1 AND'):

    pool.apply_async(bet, (adni_mprage.get(),), callback=notify)

pool.close()
pool.join()


interface.search.datatypes()
interface.search.datafields('psytool:tci_parentData')
interface.search.field_values('psytool:tci_parentData/TCI155')

a = interface.select('xnat:subjectData', ['xnat:subjectData/SUBJECT_ID', 'psytool:tci_parentData/TCI145']).where([('psytool:tci_parentData/TCI145', '=', '3'), 'AND'])
a.select(['psytool_tci_parentdata_tci145']).where(subject_id='IMAGEN_000098671905')
open('.csv', 'w').write(a.dumps())



for t in interface.select.projects().subjects('*99*').experiments('*Session*').assessors('*ADNI*').out_resources().files():
    print t

for t in interface.select('/projects/subjects/*99*/experiments/*Session*/assessors/*ADNI*/out_resources/files'):

for t in interface.select('/projects/subjects/*99*/experiments/*Session*/assessors/*ADNI*/out_resources/files').where([('psytool:tci_parentData/TCI145', '=', '3'), 'AND']):
    print t.rest.get_copy()
