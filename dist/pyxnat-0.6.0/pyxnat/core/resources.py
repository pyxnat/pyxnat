import os
import sys
import shutil
import tempfile
import mimetypes
import copy
import hashlib
import email
import csv
import re
from fnmatch import fnmatch
from StringIO import StringIO

from ..externals import httplib2
from ..externals import simplejson as json

from .uriutil import join_uri, translate_uri, uri_last, uri_nextlast, uri_parent, uri_grandparent
from .jsonutil import JsonTable, get_selection
from .attributes import EAttrs
from .cache import MultiCache, CacheManager
from .search import SearchManager, Search, build_search_document, rpn_contraints
from .help import Inspector
from .users import Users
from . import schema

DEBUG = False

# metaclasses

def get_element_from_element(rsc_name):
    def getter(self, ID):
        Element = globals()[rsc_name.title()]
        return Element(join_uri(self._uri, rsc_name+'s', ID), self._intf)
    return getter

def get_element_from_collection(rsc_name):
    def getter(self, ID):
        Element = globals()[rsc_name.title()]
        Collection = globals()[rsc_name.title()+'s']
        return Collection([Element(join_uri(eobj._uri, rsc_name+'s', ID), self._intf)
                           for eobj in self], self._intf)
    return getter

def get_collection_from_element(rsc_name):
    def getter(self, id_filter='*'):
        Collection = globals()[rsc_name.title()]
        return Collection(join_uri(self._uri, rsc_name), self._intf, id_filter)
    return getter

def get_collection_from_collection(rsc_name):
    def getter(self, id_filter='*'):
        Collection = globals()[rsc_name.title()]
        return Collection(self, self._intf, id_filter, rsc_name, self._id_header, self._columns)
    return getter


class ElementType(type):
    def __new__(cls, name, bases, dct):
        rsc_name = name.lower()+'s' \
                   if name.lower() in schema.resources_singular \
                   else name.lower()

        for child_rsc in schema.resources_tree[rsc_name]:
            dct[child_rsc] = get_collection_from_element(child_rsc)
            dct[child_rsc.rstrip('s')] = get_element_from_element(child_rsc.rstrip('s'))

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(ElementType, cls).__init__(name, bases, dct)


class CollectionType(type):
    def __new__(cls, name, bases, dct):
        rsc_name = name.lower()+'s' \
                   if name.lower() in schema.resources_singular \
                   else name.lower()

        for child_rsc in schema.resources_tree[rsc_name]:
            dct[child_rsc] = get_collection_from_collection(child_rsc)
            dct[child_rsc.rstrip('s')] = get_element_from_collection(child_rsc.rstrip('s'))

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(CollectionType, cls).__init__(name, bases, dct)

# generic classes

class EObject(object):
    """ Generic Object for an element URI.
    """
    def __init__(self, uri, interface):
        """
            Parameters
            ----------
            uri: string
                URI for an element resource. e.g. /REST/projects/my_project
            interface: :class:`Interface`
                Main interface reference.
        """
        self._uri = translate_uri(uri)
        self._urn = uri_last(self._uri)
        self._urt = uri_nextlast(self._uri)
        self._intf = interface
        self.attrs = EAttrs(self)

    def __repr__(self):
        return '<%s Object> %s'%(self.__class__.__name__, uri_last(self._uri))

    def _getcell(self, col):
        """ Gets a single property of the element resource.
        """
        return self._getcells([col])

    def _getcells(self, cols):
        """ Gets multiple properties of the element resource.
        """
        p_uri = uri_parent(self._uri)
        id_head = schema.json[self._urt][0]
        lbl_head = schema.json[self._urt][1]

        columns = [col for col in cols
                   if col not in schema.json[self._urt] or col != 'URI'] \
                  + schema.json[self._urt]

        get_id = p_uri + '?format=json&columns=%s'%','.join(columns)

        for res in self._intf._get_json(get_id):
            if self._urn in [res.get(id_head), res.get(lbl_head)]:
                if len(cols) == 1:
                    return res.get(cols[0])
                else:
                    return get_selection(res, cols)[0]

    def exists(self):
        """ Test whether an element resource exists.
        """
        try:
            return self.id() != None
        except:
            return False

    def id(self):
        """ Returns the element resource id.
        """
        return self._getcell(schema.json[self._urt][0])

    def label(self):
        """ Returns the element resource label.
        """
        return self._getcell(schema.json[self._urt][1])

    def datatype(self):
        """ Returns the type defined in the XNAT schema for this element resource.

            +----------------+-----------------------+
            | EObject        | possible xsi types    |
            +================+=======================+
            | Project        | xnat:projectData      |
            +----------------+-----------------------+
            | Subject        | xnat:subjectData      |
            +----------------+-----------------------+
            | Experiment     | xnat:mrSessionData    | 
            |                | xnat:petSessionData   | 
            +----------------+-----------------------+
        """
        return self._getcell('xsiType')

    def create(self, **datatypes):
        """ Creates the element if it does not exists.
            Any non-existing ancestor will be created as well.

            .. warning::

                An element resource both have an ID and a label that can be used
                to access it. At the moment, XNAT REST API defines the label when 
                creating an element, but not the ID, which is generated. It means
                that the `name` given to a resource may not appear when listing the
                resources because the IDs will appear, not the labels.

            Parameters
            ----------
            datatypes: keywords or dict
                Specify the datatype of the element resource and of any ancestor
                that may need to be created. The keywords correspond to the levels
                in the REST hierarchy, i.e. Interface.inspect.rest_hierarchy()

                If an element is created with no specified type:
                    - if its name matches a naming convention, this type will be used
                    - else a default type is defined in the schema module

            Examples
            --------
                >>> interface.select('/project/PROJECT/subject/SUBJECT/experiment/EXP/scan/SCAN'
                            ).create(experiments='xnat:mrSessionData', scans='xnat:mrScanData')

            See Also
            --------
            EObject.id
            EObject.label
            EObject.datatype
            Interface.inspect.naming_conventions
        """
        datatype = datatypes.get(uri_nextlast(self._uri))

        if datatype is None:
            for uri_pattern in self._intf.inspect._nomenclature.keys():
                if fnmatch(self._uri.split('/REST')[1], uri_pattern):
                    datatype = self._intf.inspect._nomenclature.get(uri_pattern)
                    break
            else:
                datatype = schema.default_datatypes.get(uri_nextlast(self._uri))

        if datatype is None:
            create_uri = self._uri
        else:
            create_uri = self._uri + '?xsiType=%s' % datatype

        parent_element = self._intf.select(uri_grandparent(self._uri))

        if not uri_nextlast(self._uri) == 'projects' \
        and not parent_element.exists():
            parent_datatype = datatypes.get(uri_nextlast(parent_element._uri))
            if DEBUG:
                print 'CREATE', parent_element, parent_datatype
            parent_element.create(**datatypes)

        if DEBUG:
            print 'PUT', create_uri
        self._intf._exec(create_uri, 'PUT')

        return self

    def delete(self, delete_files=True):
        """ Deletes an element resource.

            Parameters
            ----------
            delete_files: True | False
                Tells if files attached to the element resources are removed
                as well from the server filesystem.
        """
        delete_uri = self._uri if not delete_files \
                     else self._uri + '?removeFiles=true'

        return self._intf._exec(delete_uri, 'DELETE')

    def children(self):
        """ Returns the children levels of this element.

            Examples
            --------
            >>> subject_object.children()
            ['experiments', 'resources']
        """
        return schema.resources_tree.get(uri_nextlast(self._uri))

    def absurl(self):
        """ Returns an absolute URL of the element resource, including the
            server address and the user login and password.

            .. note::
            
                Not used at the moment.

        """
        return '%s//%s:%s@%s%s'%(self._intf._server.split('//')[0],
                                 self._intf._user,
                                 self._intf._pwd,
                                 self._intf._server.split('//')[1],
                                 self._uri
                                 )


class CObject(object):
    """ Generic Object for a collection resource.

        A collection resource is a list of element resources. There is however
        several ways to obtain such a list:
            - a collection URI e.g. /REST/projects
            - a list of element URIs
            - a list of collections e.g. /REST/projects/ONE/subjects and /REST/projects/TWO/subjects
            - a list of element objects
            - a list a collection objects

        Collections objects built in different ways share the same behavior:
            - they behave as iterators, which enables a lazy access to the data
            - they always yield EObjects
            - they can be nested with any other collection

        Examples
        --------
        No access to the data:
            >>> interface.select.projects()
            <Collection Object> 173667084
        
        Lazy access to the data:
            >>> for project in interface.select.projects():
            >>>     print project

        Nesting:
            >>> for subject in interface.select.projects().subjects():
            >>>     print subject
    """
    def __init__(self, cbase, interface, pattern='*', nested=None, 
                                                    id_header='ID', columns=[]):

        """ 
            Parameters
            ----------
            cbase: string | list | CObject
                Object from which the collection is built.
            interface: :class:`Interface`
                Main interface reference.
            pattern: string
                Only resource element whose ID match the pattern are returned.
            nested: None | string
                Parameter used to nest collections.
            id_header: ID | label
                Defines whether the element label or ID is returned as the identifier.
            columns: list
                Defines additional columns to be returned.
        """

        self._intf = interface
        self._cbase = cbase
        self._id_header = id_header
        self._pattern = pattern
        self._columns = columns
        self._nested = nested

        if isinstance(cbase, (str, unicode)):
            self._ctype = 'cobjectcuri'
        elif isinstance(cbase, CObject):
            self._ctype = 'cobjectcobject'
        elif isinstance(cbase, list) and cbase != []:
            if isinstance(cbase[0], (str, unicode)):
                self._ctype = 'cobjecteuris'
            if isinstance(cbase[0], EObject):
                self._ctype = 'cobjecteobjects'
            if isinstance(cbase[0], CObject):
                self._ctype = 'cobjectcobjects'
        elif isinstance(cbase, list) and cbase == []:
            self._ctype = 'cobjectempty'
        else:
            raise Exception('Invalid collection accessor type: %s'%cbase)

    def __repr__(self):
        return '<Collection Object> %s'%id(self)

    def _call(self, columns):
        try:
            query_string = '?format=json&columns=%s'%','.join(columns)
            return self._intf._get_json(translate_uri(self._cbase) + query_string)
        except Exception, e:
            if DEBUG:
                print e
            return []

    def __iter__(self):
        if self._ctype == 'cobjectcuri':
            if self._id_header == 'ID':
                id_header = schema.json[uri_last(self._cbase)][0]
            elif self._id_header == 'label':
                id_header = schema.json[uri_last(self._cbase)][1]
            else:
                id_header = self._id_header

            for res in self._call([id_header] + self._columns):
                try:
                    eid = res[id_header]
                    if fnmatch(eid, self._pattern):
                        Klass = globals()[uri_last(self._cbase).rstrip('s').title()]
                        eobj = Klass(join_uri(self._cbase, eid), self._intf)
                        if self._nested is None:
                            self._run_callback(self, eobj)
                            yield eobj
                        else:
                            Klass = globals()[self._nested.title()]
                            for subeobj in Klass(cbase=join_uri(eobj._uri, self._nested),
                                                 interface=self._intf, 
                                                 pattern=self._pattern, 
                                                 id_header=self._id_header, 
                                                 columns=self._columns):
                                try:
                                    self._run_callback(self, subeobj)
                                    yield subeobj
                                except RuntimeError, e:
                                    pass
                except KeyboardInterrupt:
                    self._intf._connect()
                    raise StopIteration

        elif self._ctype == 'cobjecteuris':
            for uri in self._cbase:
                try:
                    Klass = globals()[uri_nextlast(uri).rstrip('s').title()]
                    eobj = Klass(uri, self._intf)
                    if self._nested is None:
                        self._run_callback(self, eobj)
                        yield eobj
                    else:
                        Klass = globals()[self._nested.title()]
                        for subeobj in Klass(cbase=join_uri(eobj._uri, self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, subeobj)
                                yield subeobj
                            except RuntimeError, e:
                                pass
                except KeyboardInterrupt:
                    self._intf._connect()
                    raise StopIteration

        elif self._ctype == 'cobjecteobjects':
            for eobj in self._cbase:
                try:
                    if self._nested is None:
                        self._run_callback(self, eobj)
                        yield eobj
                    else:
                        Klass = globals()[self._nested.rstrip('s').title()]
                        for subeobj in Klass(cbase=join_uri(eobj._uri, self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, subeobj)
                                yield subeobj
                            except RuntimeError, e:
                                pass
                except KeyboardInterrupt:
                    self._intf._connect()
                    raise StopIteration

        elif self._ctype == 'cobjectcobject':
            for eobj in self._cbase:
                try:
                    if self._nested is None:
                        self._run_callback(self, eobj)
                        yield eobj
                    else:
                        Klass = globals()[self._nested.title()]
                        for subeobj in Klass(cbase=join_uri(eobj._uri, self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, eobj)
                                yield subeobj
                            except RuntimeError, e:
                                pass
                except KeyboardInterrupt:
                    self._intf._connect()
                    raise StopIteration

        elif self._ctype == 'cobjectcobjects':
            for cobj in self._cbase:
                try:
                    for eobj in cobj:
                        if self._nested is None:
                            self._run_callback(self, eobj)
                            yield eobj
                        else:
                            Klass = globals()[cobj._nested.title()]
                            for subeobj in Klass(cbase=join_uri(eobj._uri, cobj._nested),
                                                 interface=cobj._intf, 
                                                 pattern=cobj._pattern, 
                                                 id_header=cobj._id_header, 
                                                 columns=cobj._columns):
                                try:
                                    self._run_callback(self, eobj)
                                    yield subeobj
                                except RuntimeError, e:
                                    pass
                except KeyboardInterrupt:
                    self._intf._connect()
                    raise StopIteration

        elif self._ctype == 'cobjectempty':
            for empty in []:
                yield empty

    def _run_callback(self, cobj, eobj):
        if self._intf._callback is not None:
            self._intf._callback(cobj, eobj)

    def first(self):
        """ Returns the first element of the collection.
        """
        for eobj in self:
            return eobj

    def get(self, *args):
        """ Returns every element.

            .. warning::
                If a collection needs to issue thousands of queries it may be better
                to access the resources within a `for-loop`.

            Parameters
            ----------
            args: ID, label, obj
                Specify to return the element ID, label or Object.
                Any combination of ID, label and obj is valid, if more than one
                is given, a list of tuple is returned instead of a list.
        """
        if args == ():
            return [uri_last(eobj._uri) for eobj in self]
        else:
            ret = ()
            for arg in args:
                if arg == 'id':
                    self._id_header = 'ID'
                    ret += ([uri_last(eobj._uri) for eobj in self], )
                elif arg == 'label':
                    self._id_header = 'label'
                    ret +=  ([uri_last(eobj._uri) for eobj in self], )
                else:
                    ret += ([eobj for eobj in self], )

            if len(args) != 1:
                return ret
            else:
                return ret[0]

    def where(self, constraints):
        """ Only the element objects whose subject that are matching the 
            constraints will be returned. It means that it is not possible to
            use this method on an element that is not linked to a subject, such
            as a project.

            Examples
            --------
            The ``where`` clause should be on the first select:
                >>> for experiment in interface.select('//experiments'
                >>>                           ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>     print experiment

            Do NOT do this:
                >>> for experiment in interface.select('//experiments'):
                >>>     for assessor in experiment.assessors(
                >>>                              ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>         print assessor

            Or this:
                >>> for project in interface.select('//projects'
                >>>                        ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>     print project

            See Also
            --------
            search.Search()
        """
        if isinstance(constraints, (str, unicode)):
            constraints = rpn_contraints(constraints)

        bundle = build_search_document('xnat:subjectData', 
                                       ['xnat:subjectData/PROJECT',
                                        'xnat:subjectData/SUBJECT_ID'],
                                       constraints)

        content = self._intf._exec("/REST/search?format=json", 'POST', bundle)

        if content.startswith('<html>'):
            raise Exception(content.split('<h3>')[1].split('</h3>')[0])

        results = json.loads(content)['ResultSet']['Result']
        searchpop = ['/REST/projects/%(project)s/subjects/%(subject_id)s'%r
                     for r in results]

        cobj = self
        while cobj:
            first = cobj.first()
            if not first:
                break
 
            if uri_nextlast(first._uri) == 'subjects':
                break

            else:
                cobj = getattr(cobj, '_cbase')

        backup_header = cobj._id_header

        if cobj._pattern != '*':
            cobj._id_header = 'ID'
            poi = set(searchpop
                     ).intersection([eobj._uri for eobj in cobj])
        else:
            poi = searchpop

        cobj._cbase = list(poi)
        cobj._ctype = 'cobjecteuris'
        cobj._nested = None
        cobj._id_header = backup_header

        return self


# specialized classes

class Project(EObject):
    __metaclass__ = ElementType

    def prearchive_code(self):
        """ Gets project prearchive code.
        """
        return int(self._intf._exec(join_uri(self._uri, 'prearchive_code')))

    def set_prearchive_code(self, code):
        """ Sets project prearchive code.

            Parameters
            ----------
            code: 0 to 4
        """
        self._intf._exec(join_uri(self._uri, 'prearchive_code', code), 'PUT')

    def quarantine_code(self):
        """ Gets project quarantine code.
        """
        return int(self._intf._exec(join_uri(self._uri, 'quarantine_code')))

    def set_quarantine_code(self, code):
        """ Sets project quarantine code.

            Parameters
            ----------
            code: 0 to 1
        """
        self._intf._exec(join_uri(self._uri, 'quarantine_code', code), 'PUT')

    def current_arc(self):
        """ Gets project current archive folder on the server.
        """
        return self._intf._exec(join_uri(self._uri, 'current_arc'))

    def set_subfolder_in_current_arc(self, subfolder):
        """ Changes project current archive subfolder on the server.
        """
        current_arc = self._intf._exec(join_uri(self._uri, 'current_arc'))

        self._intf._exec(join_uri(self._uri, 'current_arc', current_arc, subfolder), 'PUT')

    def accessibility(self):
        """ Gets project accessibility.
        """
        return self._intf._exec(join_uri(self._uri, 'accessibility'), 'GET')

    def set_accessibility(self, accessibility='protected'):
        """ Sets project accessibility.

            Parameters
            ----------
            accessibility: public | protected | private
                Sets the project accessibility:
                    - public: the project is visible and provides read access 
                              for anyone.
                    - protected: the project is visible by anyone but the data 
                                 is accessible for allowed users only.
                    - private: the project is visible by allowed users only.

                Write access is given or not by the user level for a specic project.
        """
        return self._intf._exec(join_uri(self._uri, 'accessibility', 
                                         accessibility), 'PUT')

    def users(self):
        """ Gets all registered users for this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                        ).get('login', always_list=True)

    def owners(self):
        """ Gets owners of this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                        ).where(displayname='Owners').get('login', always_list=True)

    def members(self):
        """ Gets members of this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                        ).where(displayname='Members').get('login', always_list=True)

    def collaborators(self):
        """ Gets collaborator of this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                        ).where(displayname='Collaborators').get('login', always_list=True)

    def user_role(self, login):
        """ Gets the user level of the user for this project.

            Parameters
            ----------
            login: string
                A user of the project.

            Returns
            -------
            owner | member | collaborator

        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                        ).where(login=login)['displayname'].lower().rstrip('s')

    def add_user(self, login, role='member'):
        """ Adds a user to the project. The user must already exist on the server.

            Parameters
            ----------
            login: string
                Valid username for the XNAT database.
            role: owner | member | collaborator
                The user level for this project:
                    - owner: read and write access, as well as administrative privileges
                             such as adding and removing users.
                    - member: read access and can create new resources but not remove them.
                    - collaborator: read access only.
        """
        self._intf._exec(join_uri(self._uri, 'users', 
                                  role.lstrip('s').title() + 's', login), 'PUT')

    def remove_user(self, login):
        """ Removes a user from the project.

            Parameters
            ----------
            login: string
                Valid username for the XNAT database.
        """
        self._intf._exec(join_uri(self._uri, 'users',
                                  self.user_role(login).title()+'s', login),
                         'DELETE')
    
    def datatype(self):
        return 'xnat:ProjectData'

class Subject(EObject):
    __metaclass__ = ElementType

    def datatype(self):
        return 'xnat:subjectData'

    def shares(self, id_filter='*'):
        return Projects(join_uri(self._uri, 'projects'), self._intf, id_filter)

    def share(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')

class Experiment(EObject):
    __metaclass__ = ElementType

    def shares(self, id_filter='*'):
        return Projects(join_uri(self._uri, 'projects'), self._intf, id_filter)

    def share(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')

class Assessor(EObject):
    __metaclass__ = ElementType

    def shares(self, id_filter='*'):
        return Projects(join_uri(self._uri, 'projects'), self._intf, id_filter)

    def share(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')

class Reconstruction(EObject):
    __metaclass__ = ElementType

class Scan(EObject):
    __metaclass__ = ElementType

class Resource(EObject):
    __metaclass__ = ElementType

class In_Resource(Resource):
    __metaclass__ = ElementType

class Out_Resource(Resource):
    __metaclass__ = ElementType

class File(EObject):
    """ EObject for files stored in XNAT.
    """
    __metaclass__ = ElementType

    def __init__(self,  uri, interface):
        """ 
            Parameters
            ----------
            uri: string
                The file resource URI
            interface: Interface Object
        """

        EObject.__init__(self,  uri, interface)
        self._absuri = None        

    def attributes(self):
        """ Files attributes include:
                - URI
                - Name
                - Size in bytes
                - file_tags
                - file_format
                - file_content

            Returns
            -------
            A dictionnary with the file attributes.
        """

        return self._getcells(['URI', 'Name', 'Size', 
                               'file_tags', 'file_format', 'file_content'])

    def get(self):
        """ Downloads the file to the cache directory.

            .. note::
                The path is computed like this: ``path_to_cache/urichecksum_filename``

            Returns
            -------
            The location of the file in the cache directory .
        """

        if not self._absuri:
            self._absuri = self._getcell('URI')

        content = self._intf._exec(self._absuri, 'GET')
        return os.path.join(self._intf._conn.cache.cache, 
                            self._intf._conn.cache.safe(self._intf._server + self._absuri))

    def get_copy(self, dest=None):
        """ Downloads the file to the cache directory but creates a copy at
            the specified location.

            Parameters
            ----------
            dest: string | None
                Path for the copy. Defaults to None.
                If None a copy is created at a default location.

            Returns
            -------
            The location of the copy.
        """

        src = self.get()

        if not dest:
            dest = os.path.join(self._intf._conn.cache.cache, 'workspace',
                                *self._absuri.strip('/').split('/')[1:])
            
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))
        
        shutil.copy2(src, dest)

        return dest

    def put(self, src, format='U', content='U', tags='U', **datatypes):
        """ Uploads a file to XNAT.

            Parameters
            ----------
            src: string
                Location of the local file to upload.
            format: string   
                Optional parameter to specify the file format. Defaults to 'U'.
            content: string
                Optional parameter to specify the file content. Defaults to 'U'.
            tags: string
                Optional parameter to specify tags for the file. Defaults to 'U'.
        """

        format = "'%s'"%format if ' ' in format else format
        content = "'%s'"%content if ' ' in content else content
        tags = "'%s'"%tags if ' ' in tags else tags

        put_uri = "%s?format=%s&content=%s&tags=%s" % \
                            (self._uri, format, content, tags)

        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % 
                                        (os.path.basename(src), src))
        L.append('Content-Type: %s' % 
                mimetypes.guess_type(src)[0] or 'application/octet-stream')
        L.append('')
        L.append(open(src, 'rb').read())
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

        if not self._intf.select(uri_grandparent(self._uri)).exists():
            self._intf.select(uri_grandparent(self._uri)).create(**datatypes)

        self._intf._exec(self._uri, 'PUT', body, 
                         headers={'content-type':content_type})

    def create(self, src, format='U', content='U', tags='U'):
        """ Same as put.
        """
        return self.put(src, format, content, tags)

    def delete(self):
        """ Deletes the file on the server.
        """
        if not self._absuri:
            self._absuri = self._getcell('URI')
        return self._intf._exec(self._absuri, 'DELETE')

    def size(self):
        """ Gets the file size.
        """
        return self._getcell('Size')

    def tags(self):
        """ Gets the file tags.
        """
        return self._getcell('file_tags')

    def format(self):
        """ Gets the file format.
        """
        return self._getcell('file_format')

    def content(self):
        """ Gets the file content description.
        """
        return self._getcell('file_content')

    def absurl(self):
        if not self._absuri:
            self._absuri = self._getcell('URI')

        return '%s//%s:%s@%s%s'%(self._intf._server.split('//')[0],
                                 self._intf._user,
                                 self._intf._pwd,
                                 self._intf._server.split('//')[1],
                                 self._absuri
                                 )

class In_File(File):
    __metaclass__ = ElementType

class Out_File(File):
    __metaclass__ = ElementType


class Projects(CObject):
    __metaclass__ = CollectionType

class Subjects(CObject):
    __metaclass__ = CollectionType

    def sharing(self, projects=[]):
        return Subjects([eobj
                         for eobj in self
                         if set(projects).issubset(eobj.shares().get())], self._intf)

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)

class Experiments(CObject):
    __metaclass__ = CollectionType

    def sharing(self, projects=[]):
        return Experiments([eobj
                            for eobj in self
                            if set(projects).issubset(eobj.shares().get())], self._intf)

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)

class Assessors(CObject):
    __metaclass__ = CollectionType

    def sharing(self, projects=[]):
        return Assessors([eobj
                          for eobj in self
                          if set(projects).issubset(eobj.shares().get())], self._intf)

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)

class Reconstructions(CObject):
    __metaclass__ = CollectionType

class Scans(CObject):
    __metaclass__ = CollectionType

class Resources(CObject):
    __metaclass__ = CollectionType

class In_Resources(Resources):
    __metaclass__ = CollectionType

class Out_Resources(Resources):
    __metaclass__ = CollectionType

class Files(CObject):
    __metaclass__ = CollectionType

class In_Files(Files):
    __metaclass__ = CollectionType

class Out_Files(Files):
    __metaclass__ = CollectionType

