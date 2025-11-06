from pyxnat import Interface
from requests.exceptions import ConnectionError
import os.path as op
from functools import wraps
import pytest


fp = op.abspath('.devxnat.cfg')


def docker_available(func=None):
    """Skip test completely if no Docker-based XNAT instance available
    """

    def check_and_raise():
        if 'setup_docker_xnat' in func.__name__:
            print('Initializing XNAT.')
            return
        fp = op.abspath('.xnat.cfg')
        print(fp, op.isfile(fp))

        x = Interface(config=op.abspath('.xnat.cfg'))

        try:
            x.head('')
            list(x.select.projects())
            print('Docker instance found.')
        except (ConnectionError, KeyError):
            print('Skipping it.')
            pytest.skip('Docker-based XNAT instance unavailable')

    if func:
        @wraps(func)
        def newfunc(*args, **kwargs):
            check_and_raise()
            return func(*args, **kwargs)
        return newfunc
    else:
        check_and_raise()

@docker_available
def test_001_setup_docker_xnat():
    import os
    import pyxnat

    x = pyxnat.Interface(config='.xnat.cfg')

    try:
        cmd = 'curl --cookie-jar /tmp/cookie --header "Content-Type: application/x-www-form-urlencoded" '\
            '--request POST '\
            '--data "username={user}&password={password}&login=&XNAT_CSRF=" '\
            'http://localhost/login'.format(user=x._user, password=x._pwd)
        print(cmd)
        os.system(cmd)

        cmd = 'curl --cookie /tmp/cookie --header "Content-Type: application/json" '\
            '--request POST '\
            '--data \'%s\' '\
            'http://localhost/xapi/siteConfig'

        cmd2 = cmd % '{"siteId": "XNAT", "siteUrl": "http://localhost", "adminEmail": "fake@fake.fake"}'
        print(cmd2)
        os.system(cmd2)

        cmd2 = cmd % '{"archivePath":"/data/xnat/archive","prearchivePath":"/data/xnat/prearchive","cachePath":"/data/xnat/cache","buildPath":"/data/xnat/build","ftpPath":"/data/xnat/ftp","pipelinePath":"/data/xnat/pipeline","inboxPath":"/data/xnat/inbox"}'
        print(cmd2)
        os.system(cmd2)

        cmd2 = cmd % '{"requireLogin":true,"userRegistration":false,"enableCsrfToken":true}'
        print(cmd2)
        os.system(cmd2)

        cmd2 = cmd % '{"initialized":true}'
        print(cmd2)
        os.system(cmd2)

        p = x.select.project('nosetests')
        p.create()
        for i in range(3, 10):
            p = x.select.project('nosetests%s' % i)
            p.create()

        uri = '/data/projects/nosetests'
        options = {'alias': 'nosetests2'}
        data = x.put(uri, params=options).text

    except Exception:
        print('Skipping initialization.')
        pytest.skip('Docker-based XNAT initialization failed.')


@docker_available
def test_users():
    x = Interface(config='.xnat.cfg')
    assert isinstance(x.manage.users(), list)


@docker_available
def test_user_firstname():
    x = Interface(config='.xnat.cfg')
    assert x.manage.users.firstname('admin') == 'Admin'


@docker_available
def test_user_lastname():
    x = Interface(config='.xnat.cfg')
    assert x.manage.users.lastname('admin') == 'Admin'


@docker_available
def test_user_email():
    x = Interface(config='.xnat.cfg')
    assert x.manage.users.email('admin') == \
        'fake@fake.fake'


@docker_available
def test_user_id():
    x = Interface(config='.xnat.cfg')
    assert x.manage.users.id('admin') == '1'


@docker_available
def test_add_remove_user():
    x = Interface(config='.xnat.cfg')
    x.select.project('nosetests5').remove_user('admin')
    x.select.project('nosetests5').add_user('admin', 'collaborator')
    assert 'admin' in x.select.project('nosetests5').collaborators()
    x.select.project('nosetests5').remove_user('admin')
    assert 'admin' not in x.select.project('nosetests5').collaborators()
    x.select.project('nosetests5').add_user('admin', 'owner')


@docker_available
def test_project_accessibility():
    x = Interface(config='.xnat.cfg')
    print(x.select.project('nosetests5').accessibility())
    assert x.select.project('nosetests5').accessibility() in \
           [b'public', b'protected', b'private']
    x.select.project('nosetests5').set_accessibility('private')
    assert x.select.project('nosetests5').accessibility() == b'private'
    x.select.project('nosetests5').set_accessibility('protected')
    assert x.select.project('nosetests5').accessibility() == b'protected'


@docker_available
def test_create_xml():
    x = Interface(config='.xnat.cfg')
    _modulepath = op.dirname(op.abspath(__file__))
    p = x.select.project('nosetests')
    s = p.subject('10001')
    e = s.experiment('10001_MR')
    fp = op.join(_modulepath, 'sess.xml')
    assert(op.isfile(fp))
    e.create(xml=fp)
    xml = e.get().decode()
    assert('Alomar' in xml)


def test_project_users():
    x = Interface(config=fp)
    assert isinstance(x.select.project('pyxnat_tests').users(), list)


def test_project_owners():
    x = Interface(config=fp)
    assert isinstance(x.select.project('pyxnat_tests').owners(), list)


def test_project_members():
    x = Interface(config=fp)
    assert isinstance(x.select.project('pyxnat_tests').members(), list)


def test_project_collaborators():
    x = Interface(config=fp)
    assert isinstance(x.select.project('pyxnat_tests').collaborators(), list)


def test_project_user_role():
    x = Interface(config=fp)
    assert x.select.project('pyxnat_tests').user_role(x._user) == 'owner'
