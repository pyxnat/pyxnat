from uuid import uuid1

from ..pyxnat import Interface
from ..pyxnat import jsonutil

central = Interface('http://central.xnat.org', 'nosetests', 'nosetests')
search_name = uuid1().hex

def test_datatypes():
    assert 'xnat:subjectData' in central.inspect.datatypes()

def test_datafields():
    assert 'xnat:subjectData/SUBJECT_ID' in \
                    central.inspect.datatypes('xnat:subjectData')
    assert 'xnat:subjectData/SUBJECT_ID' in \
                    central.inspect.datatypes('xnat:subjectData', '*')

def test_fieldvalues():
    assert len(central.inspect.fieldvalues('xnat:subjectData/SUBJECT_ID')) != 0

def test_search():
    results = central.select('xnat:mrSessionData', 
                             central.inspect.datatypes('xnat:mrSessionData')
                    ).where([('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND'])

    assert isinstance(results, jsonutil.JsonTable)

def test_save_search():
    central.search.save(search_name, 'xnat:mrSessionData', 
                        central.inspect.datatypes('xnat:mrSessionData'),
                        [('xnat:mrSessionData/SCANNER', 'LIKE', '*GE*'), 'AND'])

    assert search_name in central.search.saved()

def test_get_search():
    results = central.search.get(search_name)
    assert isinstance(results, jsonutil.JsonTable)

def test_delete_search():
    central.search.delete(search_name)
    assert search_name not in central.search.saved()
