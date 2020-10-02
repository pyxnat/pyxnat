from pyxnat import Interface
import os.path as op
from . import skip_if_no_network

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)),
                                   'central.cfg'))

proj_1 = central.select.project('surfmask_smpl')
subj_1 = proj_1.subject('CENTRAL_S01791')
exp_1 = subj_1.experiment('CENTRAL_E04850')
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
    expected_output = '\n' + 'Project: surfmask_smpl(Surface masking samples) \
    https://central.xnat.org/data/projects/surfmask_smpl' + '\n' + 'Subjects: 43' \
                      + '\n' + 'Description: The collection of structural T1 MRI scans from &quot;Functional \
    Data for Neurosurgical Planning&quot; (IGT_FMRI_NEURO) project processed with surface \
    obscuring algorithm.' + '\n' + 'Project owners:  mmilch ' + '\n' + \
                      'Insert date: 2012-04-05 15:45:30.0' + '\n' + 'Access: public' + '\n' + 'MR experiments: 43'
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
    expected_output = '\n' + 'Subject: CENTRAL_S01791 https://central.xnat.org/data/projects/surfmask_smpl/subjects/' \
                             'CENTRAL_S01791' \
                      + '\n' + 'Project: surfmask_smpl' + '\n' + 'Insert user: mmilch' \
                      + '\n' + 'Insert date: 2012-04-10 17:27:22.0' + '\n' + 'Gender: U'
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
    expected_output = '\n' + 'Session: CENTRAL_E04850 https://central.xnat.org/data/projects/surfmask_smpl/subjects/' \
                             'CENTRAL_S01791/experiments/CENTRAL_E04850' \
                      + '\n' + 'Subject: CENTRAL_S01791' + '\n' + 'Project: surfmask_smpl' + '\n' + 'Scans: 4' \
                      + '\n' + 'Insert user: mmilch' + '\n' + 'Insert date: 2012-04-10 17:27:25.0' \
                      + '\n' + 'Date: 2008-05-06' + '\n' + 'Type: IGT_FMRI_NEURO'
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
    expected_output = '\n' + 'Scan: 11 https://central.xnat.org/data/projects/surfmask_smpl/subjects/CENTRAL_S01791' \
                             '/experiments/CENTRAL_E04850/scans/11' \
                      + '\n' + 'Experiment: CENTRAL_E04850' + '\n' + 'Type: SPGR' + '\n' + 'Frames: 175' \
                      + '\n' + 'Series Description: SPGR' + '\n' + 'Field Strength: 3.0'
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
    expected_output = '\n' + 'Resource: obscure_algorithm_output' + '\n' + 'Files: 66'
    assert list(sorted(str(resource_1))) == list(sorted(expected_output))
