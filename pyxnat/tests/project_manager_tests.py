import os
from uuid import uuid1

from .. import manage
from .. import Interface

central = Interface(config='.xnat.cfg')

def test_project_manager():
    pm = manage.ProjectManager('nosetests', central)
