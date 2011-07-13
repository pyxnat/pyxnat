import re
import glob

from lxml import etree

from .search import SearchManager
from .users import Users
from .resources import Project
from .tags import Tags
from .uriutil import join_uri, check_entry

from . import schema

def get_element_from_element(rsc_name):

    def getter(self, ID):
        Element = globals()[rsc_name.title()]

        return Element(join_uri(self._uri, rsc_name + 's', ID), self._intf)

    return getter

def get_element_from_collection(rsc_name):

    def getter(self, ID):
        Element = globals()[rsc_name.title()]
        Collection = globals()[rsc_name.title() + 's']

        return Collection([Element(join_uri(eobj._uri, rsc_name + 's', ID), 
                                   self._intf
                                   )
                           for eobj in self
                           ], 
                          self._intf
                          )
    return getter

def get_collection_from_element(rsc_name):

    def getter(self, id_filter='*'):

        Collection = globals()[rsc_name.title()]
        return Collection(join_uri(self._uri, rsc_name), 
                          self._intf, id_filter
                          )

    return getter

def get_collection_from_collection(rsc_name):

    def getter(self, id_filter='*'):
        Collection = globals()[rsc_name.title()]

        return Collection(self, self._intf, id_filter, 
                          rsc_name, self._id_header, self._columns)

    return getter


class ElementType(type):
    def __new__(cls, name, bases, dct):
        rsc_name = name.lower().split('pre')[1]+'s' \
            if name.lower().split('pre')[1] in schema.resources_singular \
            else name.lower().split('pre')[1]

        for child_rsc in schema.resources_tree[rsc_name]:
            dct[child_rsc] = get_collection_from_element(child_rsc)
            dct[child_rsc.rstrip('s')] = \
                get_element_from_element(child_rsc.rstrip('s'))

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(ElementType, cls).__init__(name, bases, dct)


class CollectionType(type):
    def __new__(cls, name, bases, dct):
        rsc_name = name.lower().split('pre')[1]+'s' \
            if name.lower().split('pre')[1] in schema.resources_singular \
            else name.lower().split('pre')[1]

        for child_rsc in schema.resources_tree[rsc_name]:
            dct[child_rsc] = get_collection_from_collection(child_rsc)
            dct[child_rsc.rstrip('s')] = \
                get_element_from_collection(child_rsc.rstrip('s'))

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(CollectionType, cls).__init__(name, bases, dct)


class GlobalManager(object):
    """ Mainly a container class to provide a clean interface for all
        management classes.
    """

    def __init__(self, interface):
        self._intf = interface

        self.search = SearchManager(self._intf)
        self.users = Users(self._intf)
        self.tags = Tags(self._intf)
        self.schemas = SchemaManager(self._intf)
        self.prearchive = PreArchive(self._intf)

    def register_callback(self, func):
        """ Defines a callback to execute when collections of resources are 
            accessed.

            Parameters
            ----------
            func: callable
                A callable that takes the current collection object as first 
                argument and the current element object as second argument.

            Examples
            --------
            >>> def notify(cobj, eobj):
            >>>    print eobj._uri
            >>> interface.manage.register_callback(notify)
        """
        self._intf._callback = func

    def unregister_callback(self):
        """ Unregisters the callback.
        """
        self._intf._callback = None

    def project(self, project_id):
        """ Returns a project manager.
        """
        return ProjectManager(project_id, self._intf)


class ProjectManager(object):
    """ Management interface for projects.

        This functionalities are also available through `Project` objects.
    """

    def __init__(self, project_id, interface):
        self._intf._get_entry_point()

        self._intf = interface
        project = Project('%s/projects/%s' % (self._intf._entry, 
                                              project_id
                                              ), 
                          self._intf
                          )

        self.prearchive_code = project.prearchive_code
        self.set_prearchive_code = project.set_prearchive_code
        self.quarantine_code = project.quarantine_code
        self.set_quarantine_code = project.set_quarantine_code
        self.current_arc = project.current_arc
        self.set_subfolder_in_current_arc = \
            project.set_subfolder_in_current_arc
        self.accessibility = project.accessibility
        self.users = project.users
        self.owners = project.owners
        self.members = project.members
        self.collaborators = project.collaborators
        self.user_role = project.user_role
        self.add_user = project.add_user
        self.remove_user = project.remove_user


class SchemaManager(object):
    """ Management interface for XNAT schemas.

        The aim is to provide a minimal set of functionalities to parse
        and look at XNAT schemas.
    """

    def __init__(self, interface):
        self._intf = interface
        self._trees = {}

    def _init(self):
        if self._trees == {}:
            cache_template = '%s/*.xsd.headers' % self._intf._cachedir

            for entry in glob.iglob(cache_template):
                hfp = open(entry, 'rb')
                content = hfp.read()
                hfp.close()

                url = re.findall('(?<=content-location:\s%s)'
                                 '.*?(?=\r{0,1}\n)' % self._intf._server, 
                                 content)[0]

                self._trees[url.split('/')[-1]] = \
                    etree.fromstring(self._intf._exec(url))

    def __call__(self):
        self._init()
        return self._trees.keys()

    def add(self, url):
        """ Loads an additional schema.

            Parameters
            ----------
            url: str
                url of the schema relative to the server.
                    e.g. for
                    http://central.xnat.org/schemas/xnat/xnat.xsd give
                    ``schemas/xnat/xnat.xsd`` or even only
                    ``xnat.xsd``

        """
        self._init()
        
        if not re.match('/?schemas/.*/.*\.xsd', url):
            if not 'schemas' in url and re.match('/?\w+/\w+[.]xsd', url):
                url = join_uri('/schemas', url)

            elif not re.match('^[^/].xsd', url):
                url = '/schemas/%s/%s'%(url.split('.xsd')[0], url)
            else:
                raise NotImplementedError
                
        self._trees[url.split('/')[-1]] = \
            etree.fromstring(self._intf._exec(url))

    def remove(self, name):
        """ Removes a schema.
        """
        if self._trees.has_key(name):
            del self._trees[name]


class PreArchive(object):

    def __init__(self, interface):
        self._intf = interface

    def project(self, project_id):
        return PreProject('/data/prearchive/projects/%s' % project_id, *
                          self._intf)

    def projects(self):
        return PreProjects('/data/prearchive/projects')


class PreEObject(object):
    
    def __init__(self, uri, interface):
        self._intf = interface
        self._uri = uri

class PreCObjects(object):
    
    def __init__(self, interface):
        self._intf = interface

class PreProjects(PreCObjects):
    __metaclass__ = CollectionType
        
class PreProject(PreEObject):
    __metaclass__ = ElementType

class PreSubjects(PreCObjects):
    __metaclass__ = CollectionType
        
class PreSubject(PreEObject):
    __metaclass__ = ElementType
        
