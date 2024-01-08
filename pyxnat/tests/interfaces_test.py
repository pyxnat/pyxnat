import os
import os.path as op
import tempfile 
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

fp = op.abspath('.central.cfg')
central = Interface(config=fp)
central_anon = Interface('https://www.nitrc.org/ir', anonymous=True)


def test_simple_object_listing():
    assert isinstance(central.select.projects().get(), list)


def test_simple_path_listing():
    assert isinstance(central.select('/projects').get(), list)


def test_nested_object_listing():
    assert isinstance(central.select.projects('*00*').subjects().get(),
                      list)


def test_nested_path_listing():
    assert isinstance(central.select('/projects/*00*/subjects').get(), list)


@skip_if_no_network
def test_search_access():
    constraints = [('xnat:subjectData/PROJECT', '=', 'ixi'),
                   'AND']

    for subject in central.select('//subjects').where(constraints):
        assert '/projects/ixi' in subject._uri


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
    with Interface(config=fp) as central_intf:
        assert central_intf.select.project('OASIS3').exists()


def test_save_config():
    central.save_config('/tmp/.xnat.cfg')

def test_save_config_home_dir():
    filename = "test_config.txt"
    with tempfile.TemporaryDirectory(dir=os.path.expanduser("~")) as tempdir:
        central.save_config(os.path.join("~", os.path.basename(tempdir), filename))
        assert os.path.exists(os.path.join(tempdir, filename))


def test_save_config_current_dir():
    filename = "test_config.txt"
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as tempdir:
        relpath = os.path.join(os.path.basename(tempdir), filename)
        central.save_config(relpath)
        assert os.path.exists(os.path.join(tempdir, filename))

@skip_if_no_network
def test_version():
    v = central.version()
    assert v['version'] == '1.7.6'


def test_login_using_explicit_credentials():
    Interface(server='http://server/',
              user='user', password='password')
