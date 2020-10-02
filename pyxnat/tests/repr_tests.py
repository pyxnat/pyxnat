from pyxnat import Interface
import os.path as op
from . import skip_if_no_network
from IPython import get_ipython

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)),
                                   'central.cfg'))

proj_1 = central.select.project('CENTRAL_OASIS_CS')
subj_1 = proj_1.subject('OAS1_0002')
exp_1 = subj_1.experiments('OAS1_0002_MR1')
scan_1 = exp_1.scan('mpr-1')
resource_1 = scan_1.resource('')

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
    expected_output_ipython = 'Project: surfmask_smpl(Surface masking samples) https://central.xnat.org/data/projects/surfmask_smpl ' \
                              'Subjects: 43' \
                              'Description: The collection of structural T1 MRI scans from &quot;Functional Data for Neurosurgical Planning&quot;' \
                              '(IGT_FMRI_NEURO) project processed with surface obscuring algorithm.' \
                              'Project owners:  mmilch' \
                              'Insert date: 2012-04-05 15:45:30.0' \
                              'Access: public' \
                              'MR experiments: 43'
    assert str(proj_1) == str(expected_output_ipython)


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
    expected_output_ipython = 'Subject: CENTRAL_S01791 https://central.xnat.org/data/projects/surfmask_smpl/subjects/CENTRAL_S01791' \
                              'Project: surfmask_smpl' \
                              'Insert user: mmilch' \
                              'Insert date: 2012-04-10 17:27:22.0' \
                              'Gender: U'
    assert str(subj_1) == str(expected_output_ipython)


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
    expected_output_ipython = 'Session: CENTRAL_E04850 https://central.xnat.org/data/experiments/CENTRAL_E04850' \
                              'Subject: CENTRAL_S01791' \
                              'Project: surfmask_smpl' \
                              'Scans: 4' \
                              'Insert user: mmilch' \
                              'Insert date: 2012-04-10 17:27:25.0' \
                              'Date: 2008-05-06' \
                              'Type: IGT_FMRI_NEURO'
    assert str(exp_1) == str(expected_output_ipython)


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
    expected_output_ipython = 'Session: 11 https://central.xnat.org/data/experiments/CENTRAL_E04850/scans/11' \
                              'Experiemnt: CENTRAL_E04850' \
                              'Type: SPGR' \
                              'Frames: 175' \
                              'Series Description: SPGR' \
                              'Field Strength: 3.0'
    assert str(scan_1) == str(expected_output_ipython)


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
def test_info_experiment():
    assert isinstance(resource_1, object)
    expected_output_ipython = 'Resource: obscure_algorithm_output ' \
                              'Number of files: 66'
    assert str(resource_1) == str(expected_output_ipython)