import os
import socket
import platform
import tempfile
from uuid import uuid1

from .. import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))

_id_set1 = {
    'sid':uuid1().hex,
    'eid':uuid1().hex,
    'aid':uuid1().hex,
    'cid':uuid1().hex,
    'rid':uuid1().hex,
    }

_id_set2 = {
    'sid':uuid1().hex,
    'eid':uuid1().hex,
    'aid':uuid1().hex,
    'cid':uuid1().hex,
    'rid':uuid1().hex,
    }

subj_1 = central.select.project('nosetests').subject(_id_set1['sid'])
expe_1 = subj_1.experiment(_id_set1['eid'])
asse_1 = expe_1.assessor(_id_set1['aid'])
scan_1 = expe_1.scan(_id_set1['cid'])
reco_1 = expe_1.reconstruction(_id_set1['rid'])

def test_subject_create():
    assert not subj_1.exists()
    subj_1.create()
    assert subj_1.exists()

def test_experiment_create():
    assert not expe_1.exists()
    expe_1.create()
    assert expe_1.exists()

def test_assessor_create():
    assert not asse_1.exists()
    asse_1.create()
    assert asse_1.exists()

def test_scan_create():
    assert not scan_1.exists()
    scan_1.create()
    assert scan_1.exists()

def test_reconstruction_create():
    assert not reco_1.exists()
    reco_1.create()
    assert reco_1.exists()

def test_provenance():
    reco_1.provenance.set({'program':'nosetests'})
    assert reco_1.provenance.get()[0]['program'] == 'nosetests'

def test_multi_create():
    asse_2 = central.select('/projects/nosetests/subjects/%(sid)s'
                            '/experiments/%(eid)s'
                            '/assessors/%(aid)s' % _id_set2
                            )

    expe_2 = central.select('/projects/nosetests/subjects/%(sid)s'
                            '/experiments/%(eid)s'%_id_set2
                            )

    assert not asse_2.exists()
    asse_2.create(experiments='xnat:petSessionData',                
                  assessors='xnat:petAssessorData')
    assert asse_2.exists()

    assert asse_2.datatype() == 'xnat:petAssessorData'
    assert expe_2.datatype() == 'xnat:petSessionData'

    scan_2 = central.select('/projects/nosetests/subjects/%(sid)s'
                            '/experiments/%(eid)s/scans/%(cid)s' % _id_set2
                            ).create()

    assert scan_2.datatype() == 'xnat:mrScanData'

#def test_share_subject():
#    assert not central.select('/projects/nosetests2'
#                              '/subjects/%(sid)s' % _id_set1
#                              ).exists()
#    subj_1.share('nosetests2')
#    assert central.select('/projects/nosetests2/subjects/%(sid)s'%_id_set1
#                              ).exists()
#    assert set(subj_1.shares().get()) == set(['nosetests', 'nosetests2'])

#def test_share_experiment():
#    assert not central.select('/projects/nosetests2/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    expe_1.share('nosetests2')
#    assert central.select('/projects/nosetests2/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    assert set(expe_1.shares().get()) == set(['nosetests', 'nosetests2'])

#def test_share_assessor():
#    assert not central.select('/projects/nosetests2/subjects/%(sid)s'
#                              '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                              ).exists()
#    asse_1.share('nosetests2')
#    assert central.select('/projects/nosetests2/subjects/%(sid)s'
#                          '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                          ).exists()
#    assert set(asse_1.shares().get()) == set(['nosetests', 'nosetests2'])

#def test_unshare_assessor():
#    asse_1.unshare('nosetests2')
#    assert not central.select('/projects/nosetests2/subjects/%(sid)s'
#                              '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                              ).exists()
#    assert asse_1.shares().get() == ['nosetests']

#def test_unshare_experiment():
#    expe_1.unshare('nosetests2')
#    assert not central.select('/projects/nosetests2/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    assert expe_1.shares().get() == ['nosetests']

#def test_unshare_subject():
#    subj_1.unshare('nosetests2')
#    assert not central.select('/projects/nosetests2/subjects/%(sid)s'%_id_set1
#                              ).exists()
#    assert subj_1.shares().get() == ['nosetests']

def test_put_file():
    local_path = os.path.join(_modulepath, 'hello_xnat.txt')
    subj_1.resource('test').file('hello.txt').put(local_path)
    assert subj_1.resource('test').file('hello.txt').exists()
    assert long(subj_1.resource('test').file('hello.txt').size()) == \
                                                os.stat(local_path).st_size

def test_get_file():
    fh = subj_1.resource('test').file('hello.txt')

    fpath = fh.get()
    assert os.path.exists(fpath)
    assert open(fpath, 'rb').read() == 'Hello XNAT!\n'

    custom = os.path.join(tempfile.gettempdir(), uuid1().hex)
    
    fh.get(custom)
    assert os.path.exists(custom), "fpath: %s custom: %s" % (fpath, custom)
    os.remove(custom)
    os.remove(fpath)

def test_put_dir_file():
    local_path = os.path.join(_modulepath, 'hello_again.txt')
    subj_1.resource('test').file('dir/hello.txt').put(local_path)
    assert subj_1.resource('test').file('dir/hello.txt').exists()
    assert long(subj_1.resource('test').file('dir/hello.txt').size()) == \
                                                os.stat(local_path).st_size

def test_get_dir_file():
    fh = subj_1.resource('test').file('dir/hello.txt')

    fpath = fh.get()
    assert os.path.exists(fpath)
    assert open(fpath, 'rb').read() == 'Hello again!\n'

    custom = os.path.join(tempfile.gettempdir(), uuid1().hex)
    
    fh.get(custom)
    assert os.path.exists(custom), "fpath: %s custom: %s" % (fpath, custom)
    os.remove(custom)
    os.remove(fpath)

def test_get_copy_file():
    fpath = os.path.join(tempfile.gettempdir(), uuid1().hex)
    fpath = subj_1.resource('test').file('hello.txt').get_copy(fpath)
    assert os.path.exists(fpath)
    fd = open(fpath, 'rb')
    assert fd.read() == 'Hello XNAT!\n'
    fd.close()
    os.remove(fpath)


def test_file_last_modified():
    f = subj_1.resource('test').file('hello.txt')
    assert isinstance(f.last_modified(), basestring)
    assert len(f.last_modified()) > 0

def test_last_modified():
    sid = subj_1.id()

    t1 = central.select('/project/nosetests').last_modified()[sid]
    subj_1.attrs.set('age', '26')
    assert subj_1.attrs.get('age') == '26'
    t2 = central.select('/project/nosetests').last_modified()[sid]

    assert t1 != t2

def test_getitem_key():
    projects = central.select.projects()
    assert projects.first().id() == projects[0].id()
    piter = projects.__iter__()
    next(piter)
    assert next(piter).id() == projects[1].id()

def test_getitem_slice():
    projects = central.select.projects()
    assert projects.first().id() == next(projects[:1]).id()
    piter = projects.__iter__()
    next(piter)
    next(piter)
    next(piter)
    for pobj in projects[3:6]:
        assert next(piter).id() == pobj.id()

def test_subject1_parent():
    project = central.select.project('nosetests')
    assert subj_1.parent()._uri == project._uri

def test_project_parent():
    project = central.select.project('nosetests')
    assert not project.parent()

def test_subject1_delete():
    assert subj_1.exists()
    subj_1.delete()
    assert not subj_1.exists()

def test_subject2_delete():
    subj_2 = central.select('/projects/nosetests/subjects/%(sid)s'%_id_set2)
    assert subj_2.exists()
    subj_2.delete()
    assert not subj_2.exists()

def test_project_configuration():
    project = central.select('/project/nosetests')
    assert project.quarantine_code() == 0
    assert project.prearchive_code() == 4, project.prearchive_code()
    assert project.current_arc() == 'arc001'
    assert 'nosetests' in project.users()
    assert 'nosetests' in project.owners()
    assert project.user_role('nosetests') == 'owner'                              
                                              
def test_put_zip():
    local_path = os.path.join(_modulepath, 'hello_dir.zip')
    assert os.path.exists(local_path)

    # Upload and confirm proper extraction
    r1 = subj_1.resource('test_zip_extract')
    r1.put_zip(local_path, extract=True)
    assert r1.exists()
    assert r1.file('hello_dir/hello_xnat_dir.txt').exists()
    assert r1.file('hello_dir/hello_dir2/hello_xnat_dir2.txt').exists()
   
    # Upload and confirm not extracted 
    r2 = subj_1.resource('test_zip_no_extract')
    r2.put_zip(local_path, extract=False)
    assert r2.exists()
    assert r2.file('hello_dir.zip').exists()
                                                                                                
def test_get_zip():
    r = subj_1.resource('test_zip_extract')
    local_dir = os.path.join(_modulepath, 'test_zip_download'+r.id())
    file_list = [os.path.join(local_dir,'test_zip_extract/hello_dir'), 
                 os.path.join(local_dir,'test_zip_extract/hello_dir/hello_xnat_dir.txt'),
                 os.path.join(local_dir,'test_zip_extract/hello_dir/hello_dir2'),
                 os.path.join(local_dir,'test_zip_extract/hello_dir/hello_dir2/hello_xnat_dir2.txt')]

    if not os.path.exists(local_dir):
        os.mkdir(local_dir)
        
    r.get(local_dir, extract=True)
    for f in file_list:
        assert os.path.exists(f)
