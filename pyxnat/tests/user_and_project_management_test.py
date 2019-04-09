import os
from .. import Interface

central = Interface(config='.xnat.cfg')

def test_users():
    assert isinstance(central.manage.users(), list)

def test_user_firstname():
    assert central.manage.users.firstname('admin') == 'Admin'

def test_user_lastname():
    assert central.manage.users.lastname('admin') == 'Admin'

def test_user_email():
    assert central.manage.users.email('admin') == \
        'fake@fake.fake'

def test_user_id():
    assert central.manage.users.id('admin') == '1'

def test_project_users():
    assert isinstance(central.select.project('nosetests').users(), list)

def test_project_owners():
    assert isinstance(central.select.project('nosetests').owners(), list)

def test_project_members():
    assert isinstance(central.select.project('nosetests').members(), list)

def test_project_collaborators():
    assert isinstance(central.select.project('nosetests').collaborators(),
                      list
                      )

def test_project_user_role():
    assert central.select.project('nosetests'
                                  ).user_role('admin') == 'owner'

def test_add_remove_user():
    central.select.project('nosetests').remove_user('admin')
    central.select.project('nosetests').add_user('admin', 'collaborator')
    assert 'admin' in central.select.project('nosetests').collaborators()
    central.select.project('nosetests').remove_user('admin')
    assert 'admin' not in central.select.project('nosetests'
                                                    ).collaborators()
    central.select.project('nosetests').add_user('admin', 'owner')

def test_project_accessibility():
    assert central.select.project('nosetests').accessibility() in \
                                        [b'public', b'protected', b'private']
    central.select.project('nosetests').set_accessibility('private')
    assert central.select.project('nosetests').accessibility() == b'private'
    central.select.project('nosetests').set_accessibility('protected')
    print(central.select.project('nosetests').accessibility())
    assert central.select.project('nosetests').accessibility() == b'protected'

def test_project_prearchive_code():
    pass

def test_project_quarantine_code():
    pass

def test_current_arc():
    pass
