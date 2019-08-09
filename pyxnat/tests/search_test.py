import os
from uuid import uuid1
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest
from .. import Interface
from .. import jsonutil

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))
search_name = uuid1().hex
search_template_name = uuid1().hex


def test_datatypes():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'xnat:subjectData' in central.inspect.datatypes()

def test_datafields():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'xnat:subjectData/DOB' in \
                    central.inspect.datatypes('xnat:subjectData')
    assert 'xnat:subjectData/DOB' in \
                    central.inspect.datatypes('xnat:subjectData', '*')

def test_fieldvalues():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert len(central.inspect.field_values('xnat:subjectData/SUBJECT_ID')
               ) != 0

def test_inspect_resources():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'OAS1_0440_MR1' in \
        central.inspect.experiment_values('xnat:mrSessionData',
                                          'CENTRAL_OASIS_CS'
                                          )

    assert 'OAS1_0286_MR1_FSEG' in \
        central.inspect.assessor_values('xnat:mrSessionData',
                                        'CENTRAL_OASIS_CS'
                                        )

    assert 'mpr-1' in \
        central.inspect.scan_values('xnat:mrSessionData',
                                        'CENTRAL_OASIS_CS'
                                        )

    # just coverage
    assert isinstance(central.inspect.experiment_types(), list)
    assert isinstance(central.inspect.assessor_types(), list)
    assert isinstance(central.inspect.scan_types(), list)
    assert isinstance(central.inspect.reconstruction_types(), list)
    assert isinstance(central.inspect.project_values(), list)
    assert isinstance(central.inspect.subject_values(), list)

def test_search():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    results = central.select(
        'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData')
        ).where([('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND'])

    assert isinstance(results, jsonutil.JsonTable)

def test_save_search():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    central.manage.search.save(
        search_name, 'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData'),
        [('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND']
        )

    assert search_name in central.manage.search.saved()

def test_get_search():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    results = central.manage.search.get(search_name)
    assert isinstance(results, jsonutil.JsonTable)

def test_delete_search():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    central.manage.search.delete(search_name)
    assert search_name not in central.manage.search.saved()

def test_save_search_template():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    central.manage.search.save_template(
        search_template_name, 'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData'),
        [('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND']
        )

    assert search_template_name in central.manage.search.saved_templates()

def test_delete_search_template():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    central.manage.search.delete_template(search_template_name)
    assert search_template_name not in \
        central.manage.search.saved_templates()
