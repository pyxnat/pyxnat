from pyxnat import manage
from pyxnat import Interface
import os.path as op

x = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))


def test_project_manager():
    manage.ProjectManager('nosetests', x)
