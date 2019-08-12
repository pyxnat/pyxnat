import socket
import platform
import tempfile
from uuid import uuid1
from six import string_types
import os.path as op
import os
from .. import Interface
from . import skip_if_no_network
from nose import SkipTest

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))
from pyxnat.core import interfaces
interfaces.STUBBORN = True

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
subj_1 = central.select.project('nosetests3').subject(_id_set1['sid'])
expe_1 = subj_1.experiment(_id_set1['eid'])
asse_1 = expe_1.assessor(_id_set1['aid'])
scan_1 = expe_1.scan(_id_set1['cid'])
reco_1 = expe_1.reconstruction(_id_set1['rid'])

@skip_if_no_network
def test_01_subject_create():
    assert not subj_1.exists()
    subj_1.create()
    assert subj_1.exists()

@skip_if_no_network
def test_02_experiment_create():
    assert not expe_1.exists()
    expe_1.create()
    assert expe_1.exists()

@skip_if_no_network
def test_03_assessor_create():
    assert not asse_1.exists()
    asse_1.create()
    assert asse_1.exists()

@skip_if_no_network
def test_04_scan_create():
    assert not scan_1.exists()
    scan_1.create()
    assert scan_1.exists()

@skip_if_no_network
def test_05_reconstruction_create():
    assert not reco_1.exists()
    reco_1.create()
    assert reco_1.exists()

# def test_provenance():
#     reco_1.provenance.set({'program':'nosetests3'})
#     assert reco_1.provenance.get()[0]['program'] == 'nosetests3'

@skip_if_no_network
def test_06_multi_create():
    asse_2 = central.select('/projects/nosetests3/subjects/%(sid)s'
                            '/experiments/%(eid)s'
                            '/assessors/%(aid)s' % _id_set2
                            )

    expe_2 = central.select('/projects/nosetests3/subjects/%(sid)s'
                            '/experiments/%(eid)s'%_id_set2
                            )

    assert not asse_2.exists()
    asse_2.create(experiments='xnat:petSessionData',
                  assessors='xnat:petAssessorData')
    assert asse_2.exists()

    assert asse_2.datatype() == 'xnat:petAssessorData'
    assert expe_2.datatype() == 'xnat:petSessionData'

    scan_2 = central.select('/projects/nosetests3/subjects/%(sid)s'
                            '/experiments/%(eid)s/scans/%(cid)s' % _id_set2
                            ).create()

    assert scan_2.datatype() == 'xnat:mrScanData'

#def test_share_subject():
#    assert not central.select('/projects/nosetests32'
#                              '/subjects/%(sid)s' % _id_set1
#                              ).exists()
#    subj_1.share('nosetests32')
#    assert central.select('/projects/nosetests32/subjects/%(sid)s'%_id_set1
#                              ).exists()
#    assert set(subj_1.shares().get()) == set(['nosetests3', 'nosetests32'])

#def test_share_experiment():
#    assert not central.select('/projects/nosetests32/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    expe_1.share('nosetests32')
#    assert central.select('/projects/nosetests32/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    assert set(expe_1.shares().get()) == set(['nosetests3', 'nosetests32'])

#def test_share_assessor():
#    assert not central.select('/projects/nosetests32/subjects/%(sid)s'
#                              '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                              ).exists()
#    asse_1.share('nosetests32')
#    assert central.select('/projects/nosetests32/subjects/%(sid)s'
#                          '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                          ).exists()
#    assert set(asse_1.shares().get()) == set(['nosetests3', 'nosetests32'])

#def test_unshare_assessor():
#    asse_1.unshare('nosetests32')
#    assert not central.select('/projects/nosetests32/subjects/%(sid)s'
#                              '/experiments/%(eid)s/assessors/%(aid)s'%_id_set1
#                              ).exists()
#    assert asse_1.shares().get() == ['nosetests3']

#def test_unshare_experiment():
#    expe_1.unshare('nosetests32')
#    assert not central.select('/projects/nosetests32/subjects/%(sid)s'
#                          '/experiments/%(eid)s'%_id_set1
#                          ).exists()
#    assert expe_1.shares().get() == ['nosetests3']

#def test_unshare_subject():
#    subj_1.unshare('nosetests32')
#    assert not central.select('/projects/nosetests32/subjects/%(sid)s'%_id_set1
#                              ).exists()
#    assert subj_1.shares().get() == ['nosetests3']

@skip_if_no_network
def test_07_put_file():
    local_path = op.join(_modulepath, 'hello_xnat.txt')
    f = subj_1.resource('test').file('hello.txt')
    subj_1.resource('test').file('hello.txt').put(local_path)
    subj_1.resource('test').put([local_path])
    assert subj_1.resource('test').file('hello.txt').exists()
    assert int(subj_1.resource('test').file('hello.txt').size()) == \
                                                os.stat(local_path).st_size
@skip_if_no_network
def test_08_get_file():
    fh = subj_1.resource('test').file('hello.txt')

    fpath = fh.get()
    assert op.exists(fpath)
    print(['toto3', open(fpath, 'rb').read()])
    try:
        assert open(fpath, 'rb').read() == bytes('Hello XNAT!%s' % os.linesep, encoding='utf8')
    except TypeError:
        pass

    custom = op.join(tempfile.gettempdir(), uuid1().hex)

    fh.get(custom)
    assert op.exists(custom), "fpath: %s custom: %s" % (fpath, custom)
    os.remove(custom)
    os.remove(fpath)

@skip_if_no_network
def test_09_put_dir_file():
    local_path = op.join(_modulepath, 'hello_again.txt')
    subj_1.resource('test').file('dir/hello.txt').put(local_path)
    assert subj_1.resource('test').file('dir/hello.txt').exists()
    assert int(subj_1.resource('test').file('dir/hello.txt').size()) == \
                                                os.stat(local_path).st_size

@skip_if_no_network
def test_10_get_dir_file():
    fh = subj_1.resource('test').file('dir/hello.txt')

    fpath = fh.get()
    assert op.exists(fpath)
    try:
        assert open(fpath, 'rb').read() == bytes('Hello again!%s' % os.linesep, encoding='utf8')
    except TypeError:
        pass

    custom = op.join(tempfile.gettempdir(), uuid1().hex)

    fh.get(custom)
    assert op.exists(custom), "fpath: %s custom: %s" % (fpath, custom)
    os.remove(custom)
    os.remove(fpath)

@skip_if_no_network
def test_11_get_copy_file():
    fpath = op.join(tempfile.gettempdir(), uuid1().hex)
    fpath = subj_1.resource('test').file('hello.txt').get_copy(fpath)
    assert op.exists(fpath)
    fd = open(fpath, 'rb')
    try:
        assert fd.read() == bytes('Hello XNAT!%s' % os.linesep, encoding='utf8')
    except TypeError:
        pass
    fd.close()
    os.remove(fpath)

@skip_if_no_network
def test_12_file_last_modified():
    f = subj_1.resource('test').file('hello.txt')
    assert isinstance(f.last_modified(), string_types)
    assert len(f.last_modified()) > 0

@skip_if_no_network
def test_13_last_modified():
    sid = subj_1.id()

    t1 = central.select('/project/nosetests3').last_modified()[sid]
    subj_1.attrs.set('age', '26')
    assert subj_1.attrs.get('age') == '26'
    t2 = central.select('/project/nosetests3').last_modified()[sid]

    assert t1 != t2

@skip_if_no_network
def test_14_getitem_key():
    projects = central.select.projects()
    assert projects.first().id() == projects[0].id()
    piter = projects.__iter__()
    next(piter)
    assert next(piter).id() == projects[1].id()

@skip_if_no_network
def test_15_getitem_slice():
    projects = central.select.projects()
    assert projects.first().id() == next(projects[:1]).id()
    piter = projects.__iter__()
    next(piter)
    next(piter)
    next(piter)
    for pobj in projects[3:6]:
        assert next(piter).id() == pobj.id()

def test_subject1_parent():
    project = central.select.project('nosetests3')
    assert subj_1.parent()._uri == project._uri

def test_project_parent():
    project = central.select.project('nosetests3')
    assert not project.parent()

@skip_if_no_network
def test_16_subject1_delete():
    assert subj_1.exists()
    subj_1.delete()
    assert not subj_1.exists()

@skip_if_no_network
def test_17_subject2_delete():
    subj_2 = central.select('/projects/nosetests3/subjects/%(sid)s'%_id_set2)
    assert subj_2.exists()
    subj_2.delete()
    assert not subj_2.exists()

@skip_if_no_network
def test_18_project_configuration():
    project = central.select('/project/nosetests3')
    version = central.version()
    from pyxnat.core.errors import DatabaseError

    try:
        assert project.quarantine_code() == 0
        assert project.prearchive_code() == 4, project.prearchive_code()
    except DatabaseError:
        if version['tag'] == '1.7.5.1':
            msg = 'Version 1.7.5.1 gives trouble on some machines. Skipping it'
            raise SkipTest(msg)

    if version['tag'] != '1.7.5.1':
        try:
            assert project.current_arc() == b'arc001'
        except DatabaseError:
            msg = 'Check if current_arc is supported in XNAT version %s.'\
                %version['tag']
            print(msg)


    assert 'nosetests' in project.users()
    assert 'nosetests' in project.owners()
    assert project.user_role('nosetests') == 'owner'

@skip_if_no_network
def test_19_put_zip():
    local_path = op.join(_modulepath, 'hello_dir.zip')
    assert op.exists(local_path)

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

@skip_if_no_network
def test_20_get_zip():
    r = subj_1.resource('test_zip_extract')
    local_dir = op.join(_modulepath, 'test_zip_download'+r.id())
    file_list = [op.join(local_dir,'test_zip_extract/hello_dir'),
                 op.join(local_dir,'test_zip_extract/hello_dir/hello_xnat_dir.txt'),
                 op.join(local_dir,'test_zip_extract/hello_dir/hello_dir2'),
                 op.join(local_dir,'test_zip_extract/hello_dir/hello_dir2/hello_xnat_dir2.txt')]

    if not op.exists(local_dir):
        os.mkdir(local_dir)

    r.get(local_dir, extract=True)
    for f in file_list:
        assert op.exists(f)
    r.get(local_dir, extract=False)

@skip_if_no_network
def test_21_project_aliases():
    project = central.select('/project/nosetests3')
    assert project.aliases() == ['nosetests32']

@skip_if_no_network
def test_22_project():
    project = central.select.project('nosetests3')
    project.datatype()
    project.experiments()
    project.experiment('nose')
