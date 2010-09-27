import re

from lxml import etree

from .search import SearchManager
from .users import Users
from .resources import Project
from .tags import Tags
from .schema import datatypes, datatype_attributes


class GlobalManager(object):
    def __init__(self, interface):
        self._intf = interface

        self.search = SearchManager(self._intf)
        self.users = Users(self._intf)
        self.tags = Tags(self._intf)
        self.schemas = SchemaManager(self._intf)

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


class SchemaManager(object):
    def __init__(self, interface):
        self._intf = interface
        self._trees = {}

    def _init(self):
        if self._trees == {}:

            for entry in self._intf.cache.entries():
                if entry.endswith('.xsd'):
                    url  = re.findall('schemas/.*', entry)[0]
                    self._trees[url.split('/')[-1]] = \
                        etree.fromstring(self._intf._exec(url))

    def load(self, url):
        """ Loads an additional schema.

            Parameters
            ----------
            url: str
                url of the schema relative to the server.
                e.g. for http://central.xnat.org/schemas/xnat/xnat.xsd
                     give schemas/xnat/xnat.xsd
        """
        self._init()
        self._trees[url.split('/')[-1]] = etree.fromstring(self._intf._exec(url))

    def names(self):
        self._init()
        return self._trees.keys()

    def docs(self):
        self._init()
        return self._trees.values()


