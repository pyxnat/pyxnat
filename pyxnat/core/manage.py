from .search import SearchManager
from .users import Users
from .resources import Project
from .tags import Tags

class GlobalManager(object):
    def __init__(self, interface):
        self._intf = interface

        self.search = SearchManager(self._intf)
        self.users = Users(self._intf)
        self.tags = Tags(self._intf)

    def project(self, project_id):
        return ProjectManager(project_id, self._intf)

class ProjectManager(object):
    def __init__(self, project_id, interface):
        self._intf = interface
        project = Project('/REST/projects/%s'%project_id, self._intf)

        self.prearchive_code = project.prearchive_code
        self.set_prearchive_code = project.set_prearchive_code
        self.quarantine_code = project.quarantine_code
        self.set_quarantine_code = project.set_quarantine_code
        self.current_arc = project.current_arc
        self.set_subfolder_in_current_arc = project.set_subfolder_in_current_arc
        self.accessibility = project.accessibility
        self.users = project.users
        self.owners = project.owners
        self.members = project.members
        self.collaborators = project.collaborators
        self.user_role = project.user_role
        self.add_user = project.add_user
        self.remove_user = project.remove_user

