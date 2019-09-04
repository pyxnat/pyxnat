import os
from .. import Interface
from requests.exceptions import ConnectionError
import os.path as op
from nose import SkipTest
from functools import wraps
from nose.plugins.attrib import attr


fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')

def docker_available(func=None):
    '''Skip test completely if no Docker-based XNAT instance available
    '''

    def check_and_raise():
        x = Interface(config='.xnat.cfg')
        try:
            x.head('')
            print('Docker instance found.')
        except ConnectionError:
            print('Skipping it.')
            raise SkipTest('Docker-based XNAT instance unavailable')

    if func:
        @wraps(func)
        @attr('network')
        @attr('docker_available')
        def newfunc(*args, **kwargs):
            check_and_raise()
            return func(*args, **kwargs)
        return newfunc
    else:
        check_and_raise()

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
    x.select.project('nosetests3').remove_user('admin')
    x.select.project('nosetests3').add_user('admin', 'collaborator')
    assert 'admin' in x.select.project('nosetests3').collaborators()
    x.select.project('nosetests3').remove_user('admin')
    assert 'admin' not in x.select.project('nosetests3'
                                                    ).collaborators()
    x.select.project('nosetests3').add_user('admin', 'owner')

@docker_available
def test_project_accessibility():
    x = Interface(config='.xnat.cfg')
    assert x.select.project('nosetests3').accessibility() in \
                                        [b'public', b'protected', b'private']
    x.select.project('nosetests3').set_accessibility('private')
    assert x.select.project('nosetests3').accessibility() == b'private'
    x.select.project('nosetests3').set_accessibility('protected')
    print(x.select.project('nosetests3').accessibility())
    assert x.select.project('nosetests3').accessibility() == b'protected'

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
