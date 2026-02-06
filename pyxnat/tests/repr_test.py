import pyxnat.core.resources
from pyxnat import Interface
import os.path as op
from pyxnat.tests import skip_if_no_network

fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)

proj_1 = central.select.project('pyxnat_tests')
subj_1 = proj_1.subject('BBRCDEV_S02627')
exp_1 = subj_1.experiment('BBRCDEV_E03106')
scan_1 = exp_1.scan('11')
resource_1 = exp_1.resource('obscure_algorithm_output')

proj_2 = central.select.project('NFB')
subj_2 = proj_2.subject('BOA')
exp_2 = subj_2.experiment('GHJ')
scan_2 = exp_2.scan('JKL')
resource_2 = scan_2.resource('IOP')


@skip_if_no_network
def test_project_exists():
    assert proj_1.exists()
    assert isinstance(proj_1, object)
    assert isinstance(proj_1, pyxnat.core.resources.Project)
    assert str(proj_1) != '<Project Object> NFB'


@skip_if_no_network
def test_project_not_exists():
    assert not proj_2.exists()
    assert isinstance(proj_2, object)
    assert isinstance(proj_2, pyxnat.core.resources.Project)
    assert str(proj_2) == '<Project Object> NFB'


@skip_if_no_network
def test_info_project():
    assert proj_1.exists()
    expected_output = (
        f'<Project Object> pyxnat_tests `pyxnat tests` (private) 3 subjects '
        f'5 MR experiments 1 CT experiment 1 PET experiment '
        f'(owner: {central._user}) (created on 2024-01-22 10:09:22.086) '
        f'{central._server}/data/projects/pyxnat_tests?format=html')
    assert str(proj_1) == expected_output


@skip_if_no_network
def test_subject_exists():
    assert subj_1.exists()
    assert isinstance(subj_1, object)
    assert isinstance(subj_1, pyxnat.core.resources.Subject)
    assert str(subj_1) != '<Subject Object> BOA'


@skip_if_no_network
def test_subject_not_exists():
    assert not subj_2.exists()
    assert isinstance(subj_2, object)
    assert isinstance(subj_2, pyxnat.core.resources.Subject)
    assert str(subj_2) == '<Subject Object> BOA'


@skip_if_no_network
def test_info_subject():
    assert subj_1.exists()
    expected_output = (
        f'<Subject Object> BBRCDEV_S02627 `001` (project: pyxnat_tests) '
        f'(Gender: U) 1 experiment {central._server}/data/projects/'
        f'pyxnat_tests/subjects/BBRCDEV_S02627?format=html')
    assert str(subj_1) == expected_output


@skip_if_no_network
def test_experiment_exists():
    assert exp_1.exists()
    assert isinstance(exp_1, object)
    assert isinstance(exp_1, pyxnat.core.resources.Experiment)
    assert str(exp_1) != '<Experiment Object> GHJ'


@skip_if_no_network
def test_experiment_not_exists():
    assert not exp_2.exists()
    assert isinstance(exp_2, object)
    assert isinstance(exp_2, pyxnat.core.resources.Experiment)
    assert str(exp_2) == '<Experiment Object> GHJ'


@skip_if_no_network
def test_info_experiment():
    assert exp_1.exists()
    expected_output = (
        f'<Experiment Object> BBRCDEV_E03106 `001_obscured` '
        f'(subject: BBRCDEV_S02627 `001`) (project: pyxnat_tests) '
        f'4 scans 1 resource (created on 2024-01-22 10:25:48.637) '
        f'{central._server}/data/projects/pyxnat_tests/subjects/'
        f'BBRCDEV_S02627/experiments/BBRCDEV_E03106?format=html')
    assert str(exp_1) == expected_output


@skip_if_no_network
def test_scan_exists():
    assert scan_1.exists()
    assert isinstance(scan_1, object)
    assert isinstance(scan_1, pyxnat.core.resources.Scan)
    assert str(scan_1) != '<Scan Object> JKL'


@skip_if_no_network
def test_scan_not_exists():
    assert not scan_2.exists()
    assert isinstance(scan_2, object)
    assert isinstance(scan_2, pyxnat.core.resources.Scan)
    assert str(scan_2) == '<Scan Object> JKL'


@skip_if_no_network
def test_info_scan():
    assert scan_1.exists()
    expected_output = (
        f'<Scan Object> 11 (`SPGR` 175 frames)  {central._server}/data/'
        f'projects/pyxnat_tests/subjects/BBRCDEV_S02627/experiments/'
        f'BBRCDEV_E03106/scans/11?format=html')
    assert str(scan_1) == expected_output


@skip_if_no_network
def test_resource_exists():
    assert resource_1.exists()
    assert isinstance(resource_1, object)
    assert isinstance(resource_1, pyxnat.core.resources.Resource)
    assert str(resource_1) != '<Resource Object> IOP'


@skip_if_no_network
def test_resource_not_exists():
    assert not resource_2.exists()
    assert isinstance(resource_2, object)
    assert isinstance(resource_2, pyxnat.core.resources.Resource)
    assert str(resource_2) == '<Resource Object> IOP'


@skip_if_no_network
def test_info_resource():
    assert resource_1.exists()
    expected_output = (
        f'<Resource Object> 19551 `obscure_algorithm_output` (66 files 2.06 GB)')
    assert str(resource_1) == expected_output


@skip_if_no_network
def test_create_delete_create():
    from uuid import uuid1
    sid = uuid1().hex
    s = proj_1.subject(sid)
    s.create()
    assert s.exists()
    s.delete()
    s.create()
    s.delete()
    assert not s.exists()
