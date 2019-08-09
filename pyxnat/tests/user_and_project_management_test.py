import os
from .. import Interface
from requests.exceptions import ConnectionError
import os.path as op
from nose import SkipTest

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')

def docker_available(f):
    x = Interface(config='.xnat.cfg')
    try:
        x.head('')
        print('Docker instance found.')
        g = f.__globals__
        g['x'] = x
    except ConnectionError:
        print('Skipping it.')
        raise SkipTest('Docker-based XNAT instance unavailable')

@docker_available
def test_users():
    assert isinstance(x.manage.users(), list)

@docker_available
def test_user_firstname():
    print(x._server)
    assert x.manage.users.firstname('admin') == 'Admin'

@docker_available
def test_user_lastname():
    assert x.manage.users.lastname('admin') == 'Admin'

@docker_available
def test_user_email():
    assert x.manage.users.email('admin') == \
        'fake@fake.fake'

@docker_available
def test_user_id():
    assert x.manage.users.id('admin') == '1'

@docker_available
def test_add_remove_user():
    x.select.project('nosetests3').remove_user('admin')
    x.select.project('nosetests3').add_user('admin', 'collaborator')
    assert 'admin' in x.select.project('nosetests3').collaborators()
    x.select.project('nosetests3').remove_user('admin')
    assert 'admin' not in x.select.project('nosetests3'
                                                    ).collaborators()
    x.select.project('nosetests3').add_user('admin', 'owner')

@docker_available
def test_project_accessibility():
    assert x.select.project('nosetests3').accessibility() in \
                                        [b'public', b'protected', b'private']
    x.select.project('nosetests3').set_accessibility('private')
    assert x.select.project('nosetests3').accessibility() == b'private'
    x.select.project('nosetests3').set_accessibility('protected')
    print(x.select.project('nosetests3').accessibility())
    assert x.select.project('nosetests3').accessibility() == b'protected'


def test_project_users():
    x = Interface(config=fp)
    assert isinstance(x.select.project('nosetests3').users(), list)

def test_project_owners():
    x = Interface(config=fp)
    assert isinstance(x.select.project('nosetests3').owners(), list)

def test_project_members():
    x = Interface(config=fp)
    assert isinstance(x.select.project('nosetests3').members(), list)

def test_project_collaborators():
    x = Interface(config=fp)
    assert isinstance(x.select.project('nosetests3').collaborators(),
                      list)

def test_project_user_role():
    x = Interface(config=fp)
    assert x.select.project('nosetests3').user_role('nosetests') == 'owner'
