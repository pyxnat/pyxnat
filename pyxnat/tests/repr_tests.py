from pyxnat import Interface
import os.path as op
from pyxnat.tests import skip_if_no_network

_modulepath = op.dirname(op.abspath(__file__))

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
print(fp)
central = Interface(config=fp)

proj_1 = central.select.project('surfmask_smpl2')
subj_1 = proj_1.subject('CENTRAL05_S01120')
exp_1 = subj_1.experiment('CENTRAL05_E02681')
scan_1 = exp_1.scan('11')
resource_1 = exp_1.resource('obscure_algorithm_output')

proj_2 = central.select.project('NFB')
subj_2 = proj_2.subject('BOA')
exp_2 = subj_2.experiment('GHJ')
scan_2 = exp_2.scan('JKL')
resource_2 = scan_2.resource('IOP')


@skip_if_no_network
def test_project_exists():
    if proj_1.exists():
        assert isinstance(proj_1, object)
        assert str(proj_1) != '<Project Object> NFB'


@skip_if_no_network
def test_project_not_exists():
    if not proj_2.exists():
        assert isinstance(proj_2, object)
        assert str(proj_2) == '<Project Object> NFB'


@skip_if_no_network
def test_info_project():
    assert isinstance(proj_1, object)
    expected_output = '<Project Object> surfmask_smpl2 `Surface masking '\
        'samples 2` (private) 1 subject 1 MR experiment (owner: nosetests) '\
        '(created on 2020-10-22 15:23:39.458) https://central.xnat.org/data/'\
        'projects/surfmask_smpl2?format=html'
    assert list(sorted(str(proj_1))) == list(sorted(expected_output))


@skip_if_no_network
def test_subject_exists():
    if subj_1.exists():
        assert isinstance(subj_1, object)
        assert str(subj_1) != '<Subject Object> BOA'


@skip_if_no_network
def test_subject_not_exists():
    if not subj_2.exists():
        assert isinstance(subj_2, object)
        assert str(subj_2) == '<Subject Object> BOA'


@skip_if_no_network
def test_info_subject():
    assert isinstance(subj_1, object)
    expected_output = '<Subject Object> CENTRAL05_S01120 `001` (project: '\
        'surfmask_smpl2) (Gender: U) 1 experiment https://central.xnat.org/'\
        'data/projects/surfmask_smpl2/subjects/CENTRAL05_S01120?format=html'
    assert list(sorted(str(subj_1))) == list(sorted(expected_output))


@skip_if_no_network
def test_experiment_exists():
    if exp_1.exists():
        assert isinstance(exp_1, object)
        assert str(exp_1) != '<Experiment Object> GHJ'


@skip_if_no_network
def test_experiment_not_exists():
    if not exp_2.exists():
        assert isinstance(exp_2, object)
        assert str(exp_2) == '<Experiment Object> GHJ'


@skip_if_no_network
def test_info_experiment():
    assert isinstance(exp_1, object)
    expected_output = '<Experiment Object> CENTRAL05_E02681 `001_obscured` (subject: '\
        'CENTRAL05_S01120 `001`) (project: surfmask_smpl2) 4 scans 1 resource '\
        '(created on 2020-10-22 15:24:30.139) https://central.xnat.org/'\
        'data/projects/surfmask_smpl2/subjects/CENTRAL05_S01120/experiments/'\
        'CENTRAL05_E02681?format=html'
    assert list(sorted(str(exp_1))) == list(sorted(expected_output))


@skip_if_no_network
def test_scan_exists():
    if scan_1.exists():
        assert isinstance(scan_1, object)
        assert str(scan_1) != '<Scan Object> JKL'


@skip_if_no_network
def test_scan_not_exists():
    if not scan_2.exists():
        assert isinstance(scan_2, object)
        assert str(scan_2) == '<Scan Object> JKL'


@skip_if_no_network
def test_info_scan():
    assert isinstance(scan_1, object)
    expected_output = '<Scan Object> 11 (`SPGR` 175 frames)  '\
        'https://central.xnat.org/data/projects/surfmask_smpl2/subjects/'\
        'CENTRAL05_S01120/experiments/CENTRAL05_E02681/scans/11?format=html'
    assert list(sorted(str(scan_1))) == list(sorted(expected_output))


@skip_if_no_network
def test_resource_exists():
    if resource_1.exists():
        assert isinstance(resource_1, object)
        assert str(resource_1) != '<Resource Object> IOP'


@skip_if_no_network
def test_resource_not_exists():
    if not resource_2.exists():
        assert isinstance(resource_2, object)
        assert str(resource_2) == '<Resource Object> IOP'


@skip_if_no_network
def test_info_resource():
    assert isinstance(resource_1, object)
    expected_output = '<Resource Object> 123361501 '\
        '`obscure_algorithm_output` (66 files 2.06 GB)'
    assert list(sorted(str(resource_1))) == list(sorted(expected_output))


@skip_if_no_network
def test_create_delete_create():
    p = central.select.project('nosetests5')
    from uuid import uuid1
    sid = uuid1().hex
    s = p.subject(sid)
    s.create()
    assert(s.exists())
    s.delete()
    s.create()
    s.delete()
    assert(not s.exists())
