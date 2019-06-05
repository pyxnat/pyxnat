import os
from .. import Interface
try:
    unicode
except NameError:
    unicode = str
fp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)
central_anon = Interface('https://central.xnat.org', anonymous=True)

def test_simple_object_listing():
    assert isinstance(central.select.projects().get(), list)

def test_simple_path_listing():
    assert isinstance(central.select('/projects').get(), list)

def test_nested_object_listing():
    assert isinstance(central.select.projects('*OASIS*').subjects().get(), list)

def test_nested_path_listing():
    assert isinstance(central.select('/projects/*OASIS*/subjects').get(), list)

# def test_nested_for_access():
#     stop = False
#     for subject in central.select('/projects/*OASIS*/subjects'):
#         for f in subject.experiments().scans().resources().files():
#             assert isinstance(f._uri, (str, unicode))
#             stop =True
#             break
#         if stop:
#             break

def test_search_access():
    constraints = [('xnat:subjectData/PROJECT', '=', 'CENTRAL_OASIS_CS'), 'AND']

    for subject in central.select('//subjects').where(constraints):
        assert '/projects/CENTRAL_OASIS_CS' in subject._uri

def test_connection_with_explicit_parameters():
    import json
    cfg = json.load(open(fp))
    x = Interface(server=cfg['server'], user=cfg['user'],
        password=cfg['password'])

def test_anonymous_access():
    projects = central_anon.select.projects().get()
    assert isinstance(projects, list)
    assert list

def test_close_jsession():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg')
    with Interface(config=config_file) as central:
        assert central.select.project('nosetests').exists()
