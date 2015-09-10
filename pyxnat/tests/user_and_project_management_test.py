import os
from .. import Interface

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))

def test_users():
    assert isinstance(central.manage.users(), list)

def test_user_firstname():
    assert central.manage.users.firstname('nosetests') == 'Yannick'

def test_user_lastname():
    assert central.manage.users.lastname('nosetests') == 'Schwartz'

def test_user_email():
    assert central.manage.users.email('nosetests') == \
        'yannick.schwartz@gmail.com'

def test_user_id():
    assert central.manage.users.id('nosetests') == '204'

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
                                  ).user_role('nosetests') == 'owner'

def test_add_remove_user():
    central.select.project('nosetests').add_user('nosetests3', 'collaborator')
    assert 'nosetests3' in central.select.project('nosetests').collaborators()
    central.select.project('nosetests').remove_user('nosetests3')
    assert 'nosetests3' not in central.select.project('nosetests'
                                                    ).collaborators()

def test_project_accessibility():
    assert central.select.project('nosetests').accessibility() in \
                                        ['public', 'protected', 'private']
    central.select.project('nosetests').set_accessibility('private')
    assert central.select.project('nosetests').accessibility() == 'private'
    central.select.project('nosetests').set_accessibility('protected')
    assert central.select.project('nosetests').accessibility() == 'protected'

def test_project_prearchive_code():
    pass

def test_project_quarantine_code():
    pass

def test_current_arc():
    pass
