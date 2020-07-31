from uuid import uuid1
from pyxnat import Interface
from pyxnat import jsonutil
import os.path as op

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)
search_name = uuid1().hex
search_template_name = uuid1().hex


def test_datatypes():
    assert 'xnat:subjectData' in central.inspect.datatypes()


def test_datafields():
    assert 'xnat:subjectData/DOB' in \
                    central.inspect.datatypes('xnat:subjectData')
    assert 'xnat:subjectData/DOB' in \
           central.inspect.datatypes('xnat:subjectData', '*')


def test_fieldvalues():
    assert len(central.inspect.field_values('xnat:subjectData/SUBJECT_ID')
               ) != 0


def test_inspect_resources():
    assert 'OAS1_0440_MR1' in \
        central.inspect.experiment_values('xnat:mrSessionData',
                                          'CENTRAL_OASIS_CS')

    assert 'OAS1_0286_MR1_FSEG' in \
        central.inspect.assessor_values('xnat:mrSessionData',
                                        'CENTRAL_OASIS_CS')

    assert 'mpr-1' in \
        central.inspect.scan_values('xnat:mrSessionData',
                                    'CENTRAL_OASIS_CS')

    # just coverage
    assert isinstance(central.inspect.experiment_types(), list)
    assert isinstance(central.inspect.assessor_types(), list)
    assert isinstance(central.inspect.scan_types(), list)
    assert isinstance(central.inspect.reconstruction_types(), list)
    assert isinstance(central.inspect.project_values(), list)
    assert isinstance(central.inspect.subject_values(), list)


def test_search():
    results = central.select(
        'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData')
        ).where([('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND'])

    assert isinstance(results, jsonutil.JsonTable)


def test_save_search():
    central.manage.search.save(
        search_name, 'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData'),
        [('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND'])

    assert search_name in central.manage.search.saved()


def test_get_search():
    results = central.manage.search.get(search_name)
    assert isinstance(results, jsonutil.JsonTable)


def test_delete_search():
    central.manage.search.delete(search_name)
    assert search_name not in central.manage.search.saved()


def test_save_search_template():
    central.manage.search.save_template(
        search_template_name, 'xnat:mrSessionData',
        central.inspect.datatypes('xnat:mrSessionData'),
        [('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND']
        )

    assert search_template_name in central.manage.search.saved_templates()


def test_delete_search_template():
    central.manage.search.delete_template(search_template_name)
    assert search_template_name not in \
        central.manage.search.saved_templates()
