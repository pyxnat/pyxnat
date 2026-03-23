from pyxnat import manage
from pyxnat import Interface
import os.path as op

central = Interface('https://www.nitrc.org/ir', anonymous=True)


def test_project_manager():
    mgmt = manage.ProjectManager('ABIDE', central)
    assert mgmt.accessibility().decode() == 'protected'
