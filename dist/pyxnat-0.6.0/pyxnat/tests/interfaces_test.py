from uuid import uuid1
from ..pyxnat import Interface

central = Interface('http://central.xnat.org', 'nosetests', 'nosetests')

def test_simple_object_listing():
    assert isinstance(central.select.projects().get(), list)

def test_simple_path_listing():
    assert isinstance(central.select('/projects').get(), list)

def test_nested_object_listing():
    assert isinstance(central.select.projects('*OASIS*').subjects().get(), list)

def test_nested_path_listing():
    assert isinstance(central.select('/projects/*OASIS*/subjects').get(), list)

def test_nested_for_access():
    stop = False
    for subject in central.select('/projects/*OASIS*/subjects'):
        for f in subject.experiments().scans().resources().files():
            assert isinstance(f._uri, (str, unicode))
            stop =True
            break
        if stop:
            break

def test_seach_access():
    constraints = [('xnat:subjectData/PROJECT', '=', 'CENTRAL_OASIS_CS'), 'AND']

    for subject in central.select('//subjects').where(constraints):
        assert '/projects/CENTRAL_OASIS_CS' in subject._uri
