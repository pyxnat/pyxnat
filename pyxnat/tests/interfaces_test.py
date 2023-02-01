import os.path as op
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)
central_anon = Interface('https://central.xnat.org', anonymous=True)


def test_simple_object_listing():
    assert isinstance(central.select.projects().get(), list)


def test_simple_path_listing():
    assert isinstance(central.select('/projects').get(), list)


def test_nested_object_listing():
    assert isinstance(central.select.projects('*OASIS*').subjects().get(),
                      list)


def test_nested_path_listing():
    assert isinstance(central.select('/projects/*OASIS*/subjects').get(), list)


@skip_if_no_network
def test_search_access():
    constraints = [('xnat:subjectData/PROJECT', '=', 'CENTRAL_OASIS_CS'),
                   'AND']

    for subject in central.select('//subjects').where(constraints):
        assert '/projects/CENTRAL_OASIS_CS' in subject._uri


def test_connection_with_explicit_parameters():
    import json
    cfg = json.load(open(fp))
    Interface(server=cfg['server'], user=cfg['user'],
              password=cfg['password'])


def test_anonymous_access():
    projects = central_anon.select.projects().get()
    assert isinstance(projects, list)
    assert list


@skip_if_no_network
def test_close_jsession():
    config_file = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
    with Interface(config=config_file) as central:
        assert central.select.project('nosetests').exists()


def test_save_config():
    central.save_config('/tmp/.xnat.cfg')


@skip_if_no_network
def test_version():
    v = central.version()
    assert(v['version'] == '1.7.5.2-SNAPSHOT')


def test_login_using_explicit_credentials():
    Interface(server='http://server/',
              user='user', password='password')
