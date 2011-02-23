from __future__ import with_statement

import os
import shutil
import tempfile
import mimetypes
import zipfile
import time
import urllib
from fnmatch import fnmatch

from ..externals import simplejson as json

from .uriutil import join_uri, translate_uri, uri_segment
from .uriutil import uri_last, uri_nextlast
from .uriutil import uri_parent, uri_grandparent
from .uriutil import uri_shape

from .jsonutil import JsonTable, get_selection
from .pathutil import find_files
from .attributes import EAttrs
from .search import build_search_document, rpn_contraints
from .errors import is_xnat_error, parse_put_error_message
from .cache import md5name
from . import schema

DEBUG = False

# metaclasses

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
        rsc_name = name.lower()+'s' \
            if name.lower() in schema.resources_singular \
            else name.lower()

        for child_rsc in schema.resources_tree[rsc_name]:
            dct[child_rsc] = get_collection_from_element(child_rsc)
            dct[child_rsc.rstrip('s')] = \
                get_element_from_element(child_rsc.rstrip('s'))

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
            dct[child_rsc.rstrip('s')] = \
                get_element_from_collection(child_rsc.rstrip('s'))

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
                URI for an element resource. 
                e.g. /REST/projects/my_project

            interface: :class:`Interface`
                Main interface reference.
        """
        self._uri = urllib.quote(translate_uri(uri))
        self._urn = urllib.unquote(uri_last(self._uri))
        self._urt = uri_nextlast(self._uri)
        self._intf = interface
        self.attrs = EAttrs(self)

    def __repr__(self):
        return '<%s Object> %s' % (self.__class__.__name__, 
                                   urllib.unquote(uri_last(self._uri))
                                   )

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
        filters = {}

        columns = set([col for col in cols
                       if col not in schema.json[self._urt] \
                           or col != 'URI'] + schema.json[self._urt]
                      )

        get_id = p_uri + '?format=json&columns=%s' % ','.join(columns)

        for pattern in self._intf._struct.keys():
            print uri_segment(self._uri.split('/REST')[1], -2), pattern

            if fnmatch(uri_segment(self._uri.split('/REST')[1], -2), 
                       pattern):

                reg_pat = self._intf._struct[pattern]
                filters.setdefault('xsiType', set()).add(reg_pat)

        if filters != {}:
            get_id += '&' + \
                '&'.join('%s=%s' % (item[0], item[1]) 
                         if isinstance(item[1], basestring) 
                         else '%s=%s' % (item[0], 
                                         ','.join([val for val in item[1]])
                                         )
                         for item in filters.items()
                         )

        for res in self._intf._get_json(get_id):
            if self._urn in [res.get(id_head), res.get(lbl_head)]:
                if len(cols) == 1:
                    return res.get(cols[0])
                else:
                    return get_selection(res, cols)[0]

    def exists(self, consistent=False):
        """ Test whether an element resource exists.
        """
        try:
            return self.id() != None
        except Exception, e:
            if DEBUG:
                print e
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
        """ Returns the type defined in the XNAT schema for this element 
        resource.

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

    def create(self, **params):
        """ Creates the element if it does not exists.
            Any non-existing ancestor will be created as well.

            .. warning::
                An element resource both have an ID and a label that
                can be used to access it. At the moment, XNAT REST API
                defines the label when creating an element, but not
                the ID, which is generated. It means that the `name`
                given to a resource may not appear when listing the
                resources because the IDs will appear, not the labels.

            .. note::
               To set up additional variables for the element at its
               creation it is possible to use shortcuts defined in the
               XNAT REST documentation or xpath in the schema:
                   - element.create(ID='theid')
                   - subject.create(**{'xnat:subjectData/ID':'theid'})


            Parameters
            ----------
            params: keywords
                - Specify the datatype of the element resource and of
                  any ancestor that may need to be created. The
                  keywords correspond to the levels in the REST
                  hierarchy, see Interface.inspect.architecture()
                - If an element is created with no specified type:
                      - if its name matches a naming convention, this type 
                        will be used
                      - else a default type is defined in the schema module

            Examples
            --------
                >>> interface.select('/project/PROJECT/subject'
                                     '/SUBJECT/experiment/EXP/scan/SCAN'
                            ).create(experiments='xnat:mrSessionData', 
                                     scans='xnat:mrScanData'
                                     )

            See Also
            --------
            EObject.id
            EObject.label
            EObject.datatype
        """
        datatype = params.get(uri_nextlast(self._uri))
        struct = self._intf._struct

        if datatype is None:
            for uri_pattern in struct.keys():
                if fnmatch(self._uri.split('/REST')[1], uri_pattern):
                    datatype = struct.get(uri_pattern)
                    break
            else:
                datatype = schema.default_datatypes.get(
                    uri_nextlast(self._uri))

        if datatype is None:
            create_uri = self._uri
        else:
            local_params = \
                [param for param in params
                 if param not in schema.resources_types \
                     and (param.startswith(datatype) or '/' not in param)
                 ]

            create_uri = '%s?xsiType=%s' % (self._uri, datatype)

            if 'ID' not in local_params \
                    and '%s/ID' % datatype not in local_params:

                create_uri += '&%s/ID=%s' % (datatype, uri_last(self._uri))

            if local_params != []:
                create_uri += '&' + '&'.join('%s=%s' % (key, 
                                                        params.get(key)
                                                        ) 
                                             for key in local_params
                                             )

            # avoid to reuse relative parameters
            for key in local_params:
                del params[key]

        parent_element = self._intf.select(uri_grandparent(self._uri))

        if not uri_nextlast(self._uri) == 'projects' \
                and not parent_element.exists():
            
            parent_datatype = params.get(uri_nextlast(parent_element._uri))
            if DEBUG:
                print 'CREATE', parent_element, parent_datatype
            parent_element.create(**params)

        if DEBUG:
            print 'PUT', create_uri
        
        output = self._intf._exec(create_uri, 'PUT')

        if is_xnat_error(output):
            paths = []
            print output
            for datatype_name, element_name \
                    in parse_put_error_message(output):

                path = self._intf.inspect.schemas.look_for(
                    element_name, datatype_name)

                paths.extend(path)

                if DEBUG:
                    print path, 'is required'

            return paths

        return self

    insert = create

    def delete(self, delete_files=True):
        """ Deletes an element resource.

            Parameters
            ----------
            delete_files: boolean
                Tells if files attached to the element resources are
                removed as well from the server filesystem.
        """
        delete_uri = self._uri if not delete_files \
            else self._uri + '?removeFiles=true'

        return self._intf._exec(delete_uri, 'DELETE')

    def get(self):
        """ Retrieves the XML document corresponding to this element.
        """
        return self._intf._exec(self._uri+'?format=xml', 'GET')

    def children(self, show_names=True):
        """ Returns the children levels of this element.

            Parameters
            ----------
            show_name: boolean
                If True returns a list of strings. If False returns a
                collection object referencing all child objects of
                this elements.

            Examples
            --------
            >>> subject_object.children()
            ['experiments', 'resources']
            >>> subject_object.children(False)
            <Collection Object> 170976556
        """
        children = schema.resources_tree.get(uri_nextlast(self._uri))

        if show_names:
            return children

        return CObject([getattr(self, child)() for child in children], 
                       self._intf
                       )
             
    def tag(self, name):
        """ Tag the element.
        """
        tag = self._intf.manage.tags.get(name)
        if not tag.exists():
            tag.create()

        tag.reference(self._uri)
        return tag

    def untag(self, name):
        """ Remove a tag for the element.
        """
        tag = self._intf.manage.tags.get(name)
        tag.dereference(self._uri)
        if tag.references().get() == []:
            tag.delete()


class CObject(object):
    """ Generic Object for a collection resource.

        A collection resource is a list of element resources. There is 
        however several ways to obtain such a list:
            - a collection URI e.g. /REST/projects
            - a list of element URIs
            - a list of collections 
               e.g. /REST/projects/ONE/subjects **AND** 
               /REST/projects/TWO/subjects
            - a list of element objects
            - a list a collection objects

        Collections objects built in different ways share the same behavior:
            - they behave as iterators, which enables a lazy access to 
              the data
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
                            id_header='ID', columns=[], filters={}):

        """ 
            Parameters
            ----------
            cbase: string | list | CObject
                Object from which the collection is built.
            interface: :class:`Interface`
                Main interface reference.
            pattern: string
                Only resource element whose ID match the pattern are 
                returned.
            nested: None | string
                Parameter used to nest collections.
            id_header: ID | label
                Defines whether the element label or ID is returned as the 
                identifier.
            columns: list
                Defines additional columns to be returned.
            filters: dict
                Defines additional filters for the query, typically options
                for the query string.
        """

        self._intf = interface
        self._cbase = cbase
        self._id_header = id_header
        self._pattern = pattern
        self._columns = columns
        self._filters = filters
        self._nested = nested

        if isinstance(cbase, basestring):
            self._ctype = 'cobjectcuri'
        elif isinstance(cbase, CObject):
            self._ctype = 'cobjectcobject'
        elif isinstance(cbase, list) and cbase != []:
            if isinstance(cbase[0], basestring):
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
        return '<Collection Object> %s' % id(self)

    def _call(self, columns):
        try:
            uri = translate_uri(self._cbase)
            uri = urllib.quote(uri)

            request_shape = uri_shape('%s/0' % uri.split('/REST')[1])
            reqcache = os.path.join(self._intf._cachedir, 
                                   '%s.struct' % md5name(request_shape)
                                   ).replace('_*', '')

            gather = uri.split('/')[-1] in ['experiments', 'assessors', 
                                            'scans', 'reconstructions']

            tick = time.gmtime(time.time())[5] % \
                self._intf.inspect._tick == 0 and\
                self._intf.inspect._auto

            if (not os.path.exists(reqcache) and gather) \
                    or (gather and tick):

                columns += ['xsiType']

                # struct = {}
            # if self._intf._struct.has_key(reqcache):
            #     struct = self._intf._struct[reqcache]
            # else:
            #     struct = json.load(open(reqcache, 'rb'))
                # self._intf._struct[reqcache] = struct

            query_string = '?format=json&columns=%s' % ','.join(columns)

            # struct = {}

            # for pattern in struct.keys():
            #     request_pat = uri_segment(
            #         join_uri(uri, self._pattern).split('/REST')[1], -2
            #         )

            #     # print pattern, request_pat, fnmatch(pattern, request_pat)
                                              
            #     if (fnmatch(pattern, request_pat) 
            #         and struct[pattern] is not None):

            #         self._filters.setdefault('xsiType', set()
            #                                  ).add(struct[pattern])

            # if self._filters != {}:
            #     query_string += '&' + \
            #         '&'.join('%s=%s' % (item[0], item[1]) 
            #                  if isinstance(item[1], (str, unicode)) 
            #                  else '%s=%s' % (item[0], 
            #                                  ','.join([val 
            #                                            for val in item[1]
            #                                            ])
            #                                  )
            #                  for item in self._filters.items()
            #                  )

            jtable = self._intf._get_json(uri + query_string)

            if (not os.path.exists(reqcache) and gather) \
                    or (gather and tick):

                _type = uri.split('/')[-1]
                self._learn_from_table(_type, jtable, reqcache)

            return jtable
        except Exception, e:
            if DEBUG:
                raise e
            return []

    def _learn_from_table(self, _type, jtable, reqcache):
        request_knowledge = {}

        for element in jtable:
            xsitype = element.get('xsiType')
            uri = element.get('URI').split('/REST')[1]
            uri = uri.replace(uri.split('/')[-2], _type)
            shape = uri_shape(uri)

            request_knowledge[shape] = xsitype

        if os.path.exists(reqcache):
            previous = json.load(open(reqcache, 'rb'))
            previous.update(request_knowledge)
            request_knowledge = previous

        self._intf._struct.update(request_knowledge)

        json.dump(request_knowledge, open(reqcache, 'w'))

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
                    eid = urllib.unquote(res[id_header])
                    if fnmatch(eid, self._pattern):
                        klass_name = uri_last(self._cbase
                                              ).rstrip('s').title()
                        Klass = globals()[klass_name]
                        eobj = Klass(join_uri(self._cbase, eid), self._intf)
                        if self._nested is None:
                            self._run_callback(self, eobj)
                            yield eobj
                        else:
                            Klass = globals()[self._nested.title()]
                            for subeobj in Klass(cbase=join_uri(eobj._uri, 
                                                                self._nested
                                                                ),
                                                 interface=self._intf, 
                                                 pattern=self._pattern, 
                                                 id_header=self._id_header, 
                                                 columns=self._columns):
                                try:
                                    self._run_callback(self, subeobj)
                                    yield subeobj
                                except RuntimeError:
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
                        for subeobj in Klass(cbase=join_uri(eobj._uri, 
                                                            self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, subeobj)
                                yield subeobj
                            except RuntimeError:
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
                        for subeobj in Klass(cbase=join_uri(eobj._uri, 
                                                            self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, subeobj)
                                yield subeobj
                            except RuntimeError:
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
                        for subeobj in Klass(cbase=join_uri(eobj._uri, 
                                                            self._nested),
                                             interface=self._intf, 
                                             pattern=self._pattern, 
                                             id_header=self._id_header, 
                                             columns=self._columns):
                            try:
                                self._run_callback(self, eobj)
                                yield subeobj
                            except RuntimeError:
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
                            for subeobj in Klass(
                                cbase=join_uri(eobj._uri, cobj._nested),
                                interface=cobj._intf, 
                                pattern=cobj._pattern, 
                                id_header=cobj._id_header, 
                                columns=cobj._columns):
                                
                                try:
                                    self._run_callback(self, eobj)
                                    yield subeobj
                                except RuntimeError:
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

    fetchone = first

    def get(self, *args):
        """ Returns every element.

            .. warning::
                If a collection needs to issue thousands of queries it may 
                be better to access the resources within a `for-loop`.

            Parameters
            ----------
            args: strings
                - Specify the information to return for the elements
                  within ID, label and Object.
                - Any combination of ID, label and obj is valid, if
                  more than one is given, a list of tuple is returned
                  instead of a list.
        """
        if args == ():
            return [urllib.unquote(uri_last(eobj._uri)) for eobj in self]
        else:
            ret = ()
            for arg in args:
                if arg == 'id':
                    self._id_header = 'ID'
                    ret += ([urllib.unquote(uri_last(eobj._uri)) 
                             for eobj in self
                             ], )
                elif arg == 'label':
                    self._id_header = 'label'
                    ret +=  ([urllib.unquote(uri_last(eobj._uri)) 
                              for eobj in self
                              ], )
                else:
                    ret += ([eobj for eobj in self], )

            if len(args) != 1:
                return ret
            else:
                return ret[0]

    fetchall = get

    def tag(self, name):
        """ Tag the collection.
        """
        tag = self._intf.manage.tags.get(name)
        if not tag.exists():
            tag.create()

        tag.reference_many([eobj._uri for eobj in self])
        return tag

    def untag(self, name):
        """ Remove the tag from the collection.
        """
        tag = self._intf.manage.tags.get(name)
        tag.dereference_many([eobj._uri for eobj in self])
        if tag.references().get() == []:
            tag.delete()

    def where(self, constraints):
        """ Only the element objects whose subject that are matching the 
            constraints will be returned. It means that it is not possible 
            to use this method on an element that is not linked to a 
            subject, such as a project.

            Examples
            --------
            The ``where`` clause should be on the first select:
                >>> for experiment in interface.select('//experiments'
                         ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>      print experiment

            Do **NOT** do this:
                >>> for experiment in interface.select('//experiments'):
                        for assessor in experiment.assessors(
                            ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>         print assessor

            Or this:
                >>> for project in interface.select('//projects'
                        ).where([('atest/FIELD', '=', 'value'), 'AND']):
                >>>     print project

            See Also
            --------
            search.Search()
        """
        if isinstance(constraints, basestring):
            constraints = rpn_contraints(constraints)

        bundle = build_search_document('xnat:subjectData', 
                                       ['xnat:subjectData/PROJECT',
                                        'xnat:subjectData/SUBJECT_ID'
                                        ],
                                       constraints
                                       )

        content = self._intf._exec("/REST/search?format=json", 
                                   'POST', bundle)

        if content.startswith('<html>'):
            raise Exception(content.split('<h3>')[1].split('</h3>')[0])

        results = json.loads(content)['ResultSet']['Result']
        searchpop = ['/REST/projects/%(project)s'
                     '/subjects/%(subject_id)s' % res
                     for res in results
                     ]

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
        self._intf._exec(join_uri(self._uri, 'prearchive_code', code), 
                         'PUT')

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
        self._intf._exec(join_uri(self._uri, 'quarantine_code', code), 
                         'PUT')

    def current_arc(self):
        """ Gets project current archive folder on the server.
        """
        return self._intf._exec(join_uri(self._uri, 'current_arc'))

    def set_subfolder_in_current_arc(self, subfolder):
        """ Changes project current archive subfolder on the server.
        """
        current_arc = self._intf._exec(join_uri(self._uri, 'current_arc'))

        self._intf._exec(join_uri(self._uri, 'current_arc', 
                                  current_arc, subfolder), 
                         'PUT')

    def accessibility(self):
        """ Gets project accessibility.
        """
        return self._intf._exec(join_uri(self._uri, 'accessibility'), 'GET')

    def set_accessibility(self, accessibility='protected'):
        """ Sets project accessibility.

            .. note::
                Write access is given or not by the user level for a 
                specific project.

            Parameters
            ----------
            accessibility: public | protected | private
                Sets the project accessibility:
                    - public: the project is visible and provides read 
                      access for anyone.
                    - protected: the project is visible by anyone but the 
                      data is accessible for allowed users only.
                    - private: the project is visible by allowed users only.

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
                         ).where(displayname='Owners'
                                 ).get('login', always_list=True)

    def members(self):
        """ Gets members of this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                         ).where(displayname='Members'
                                 ).get('login', always_list=True)

    def collaborators(self):
        """ Gets collaborator of this project.
        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                         ).where(displayname='Collaborators'
                                 ).get('login', always_list=True)

    def user_role(self, login):
        """ Gets the user level of the user for this project.

            Parameters
            ----------
            login: string
                A user of the project.

            Returns
            -------
            string : owner | member | collaborator

        """
        return JsonTable(self._intf._get_json(join_uri(self._uri, 'users'))
                         ).where(login=login
                                 )['displayname'].lower().rstrip('s')

    def add_user(self, login, role='member'):
        """ Adds a user to the project. The user must already exist on 
            the server.

            Parameters
            ----------
            login: string
                Valid username for the XNAT database.
            role: owner | member | collaborator
                The user level for this project:
                    - owner: read and write access, as well as 
                      administrative privileges such as adding and removing
                      users.
                    - member: read access and can create new resources but 
                      not remove them.
                    - collaborator: read access only.
        """
        self._intf._exec(join_uri(self._uri, 'users', 
                                  role.lstrip('s').title() + 's', 
                                  login
                                  ), 
                         'PUT')

    def remove_user(self, login):
        """ Removes a user from the project.

            Parameters
            ----------
            login: string
                Valid username for the XNAT database.
        """
        self._intf._exec(join_uri(self._uri, 'users',
                                  self.user_role(login).title()+'s', 
                                  login
                                  ),
                         'DELETE')

    def datatype(self):
        return 'xnat:projectData'

    def experiments(self, id_filter='*'):
        return Experiments('/REST/experiments', self._intf, id_filter, 
                           filters={'project':self.id()}
                           )

    def experiment(self, ID):
        return Experiment('/REST/experiments/%s' % ID, self._intf)

    def last_modified(self):
        """ Gets the last modified dates for all the project subjects.

            If any element related to a subject changes, experiment,
            variable, scan, image etc... the date will be changed.
        """
        uri = '%s/subjects?columns=last_modified' % self._uri

        return dict(JsonTable(self._intf._get_json(uri), 
                              order_by=['ID', 'last_modified']
                              ).select(['ID', 'last_modified']
                                       ).items()
                    )
            

class Subject(EObject):
    __metaclass__ = ElementType

    def datatype(self):
        return 'xnat:subjectData'

    def shares(self, id_filter='*'):
        """ Returns the projects sharing this subject.

            Returns
            -------
            Collection object.
        """
        return Projects(join_uri(self._uri, 'projects'), 
                        self._intf, id_filter)

    def share(self, project):
        """ Share this subject with another project.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        """ Remove subject from another project in which it was shared.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')


class Experiment(EObject):
    __metaclass__ = ElementType

    def shares(self, id_filter='*'):
        """ Returns the projects sharing this experiment.

            Returns
            -------
            Collection object.
        """
        return Projects(join_uri(self._uri, 'projects'), 
                        self._intf, id_filter)

    def share(self, project):
        """ Share this experiment with another project.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        """ Remove experiment from another project in which it was shared.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')

    def trigger_pipelines(self):
        """ Triggers the AutoRun pipeline.
        """
        self._intf._exec(self._uri+'?triggerPipelines=true', 'PUT')

    def fix_scan_types(self):
        """ Populate empty scan TYPE attributes based on how similar 
            scans were populated.
        """
        self._intf._exec(self._uri+'?fixScanTypes=true', 'PUT')

    def pull_data_from_headers(self):
        """ Pull DICOM header values into the session.
        """
        self._intf._exec(self._uri+'?pullDataFromHeaders=true', 'PUT')

    def trigger(self, pipelines=True, fix_types=True, scan_headers=True):
        """ Run several triggers in a single call.
            
            Parameters
            ----------
            pipelines: boolean
                Same as trigger_pipelines.
            fix_types: boolean
                Same as fix_scan_types.
            scan_headers: boolean
                Same as pull_data_from headers.
        """
        if not all([not pipelines, not fix_types, not scan_headers]):
            options = []
            if pipelines:
                options.append('triggerPipelines=true')
            if fix_types:
                options.append('fixScanTypes=true')
            if scan_headers:
                options.append('pullDataFromHeaders=true')

            options = '?' + '&'.join(options)
    
            self._intf._exec(self._uri + options, 'PUT')


class Assessor(EObject):
    __metaclass__ = ElementType

    def shares(self, id_filter='*'):
        """ Returns the projects sharing this assessor.

            Returns
            -------
            Collection object.
        """
        return Projects(join_uri(self._uri, 'projects'), 
                        self._intf, id_filter)

    def share(self, project):
        """ Share this assessor with another project.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'PUT')

    def unshare(self, project):
        """ Remove assessor from another project in which it was shared.

            Parameters
            ----------
                project: string
                    The other project name.
        """
        self._intf._exec(join_uri(self._uri, 'projects', project), 'DELETE')


class Reconstruction(EObject):
    __metaclass__ = ElementType

class Scan(EObject):
    __metaclass__ = ElementType


class Resource(EObject):
    __metaclass__ = ElementType

    def get(self, dest_dir, extract=False):
        """ Downloads all the files within a resource.

            ..warning::
                Currently XNAT adds parent folders in the zip file that
                is downloaded to avoid name clashes if several resources
                are downloaded in the same folder. In order to be able to
                download the data uploaded previously with the same
                structure, pyxnat extracts the zip file, remove the exra
                paths and if necessary re-zips it. Careful, it may take
                time, and there is the problem of name clashes.

            Parameters
            ----------
            dest_dir: string
                Destination directory for the resource data.
            extract: boolean
                If True, the downloaded zip file is extracted.
                If False, not extracted.
                
            Returns
            -------
            If extract is False, the zip file path.
            If extract is True, the list of file paths previously in 
            the zip.
        """
        zip_location = os.path.join(dest_dir, uri_last(self._uri) + '.zip')

        if dest_dir is not None:
            self._intf._conn.cache.preset(zip_location)

        self._intf._exec(join_uri(self._uri, 'files')+'?format=zip')

        fzip = zipfile.ZipFile(zip_location, 'r')
        fzip.extractall(path=dest_dir)
        fzip.close()

        members = []            

        for member in fzip.namelist():
            old_path = os.path.join(dest_dir, member)
            new_path = os.path.join(
                dest_dir, 
                uri_last(self._uri), 
                member.split('files', 1)[1].split(os.sep, 2)[2])

            if not os.path.exists(os.path.dirname(new_path)):
                os.makedirs(os.path.dirname(new_path))

            shutil.move(old_path, new_path)

            members.append(new_path)

        # TODO: cache.delete(...)
        for extracted in fzip.namelist():
            pth = os.path.join(dest_dir, extracted.split(os.sep, 1)[0])

            if os.path.exists(pth):
                shutil.rmtree(pth)

        os.remove(zip_location)

        if not extract:
            fzip = zipfile.ZipFile(zip_location, 'w')
            arcprefix = os.path.commonprefix(members)
            arcroot = '/%s' % os.path.split(arcprefix.rstrip('/'))[1]

            for member in members:
                fzip.write(member, os.path.join(arcroot, 
                                                member.split(arcprefix)[1])
                           )
            fzip.close()

            shutil.rmtree(os.path.join(dest_dir, uri_last(self._uri)))

        return zip_location if os.path.exists(zip_location) else members

    def put(self, sources, **datatypes):
        """ Insert a list of files in a single resource element.

            This method takes all the files an creates a zip with them
            which will be the element to be uploaded and then extracted on
            the server.
        """
        zip_location = tempfile.mkstemp(suffix='.zip')[1]
        
        arcprefix = os.path.commonprefix(sources)
        arcroot = '/%s' % os.path.split(arcprefix.rstrip('/'))[1]

        fzip = zipfile.ZipFile(zip_location, 'w')
        for src in sources:
            fzip.write(src, os.path.join(arcroot, src.split(arcprefix)[1]))

        fzip.close()

        self.put_zip(zip_location, **datatypes)
        os.remove(zip_location)

    def put_zip(self, zip_location, **datatypes):
        """ Uploads a zip file an then extracts it on the server.

            After the zip file is extracted the files are accessible
            individually, or as a whole using get_zip.
        """
        if not self.exists():
            self.create(**datatypes)

        self.file(os.path.split(zip_location)[1] + '?extract=true'
                  ).put(zip_location)
        
    def put_dir(self, src_dir, **datatypes):
        """ Finds recursively all the files in a folder and uploads
            them using `insert`.
        """
        self.put(find_files(src_dir), **datatypes)

    insert = put
    insert_zip = put_zip
    insert_dir = put_dir

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
            dict : a dictionnary with the file attributes
        """

        return self._getcells(['URI', 'Name', 'Size', 
                               'file_tags', 'file_format', 'file_content'])

    def get(self, dest=None):
        """ Downloads the file to the cache directory.

            .. note::
                The default cache path is computed like this: 
                ``path_to_cache/md5(uri + query_string)_filename``

            Parameters
            ----------
            dest: string | None
                - If None a default path in the cache folder is
                  automatically computed. 
                - Else the file is downloaded at the requested location.

            Returns
            -------
            string : the file location.
        """

        start = time.time()

        if not self._absuri:
            self._absuri = self._getcell('URI')

        if dest is not None:
            self._intf._conn.cache.preset(dest)

        self._intf._exec(self._absuri, 'GET')

        print time.time() - start

        return self._intf._conn.cache.get_diskpath(self._intf._server + \
                                                       self._absuri)

    def get_copy(self, dest=None):
        """ Downloads the file to the cache directory but creates a copy at
            the specified location.

            Parameters
            ----------
            dest: string | None
                - file path for the copy
                - if None a copy is created at a default location based
                  on the file URI on the server

            Returns
            -------
            string : the copy location.
        """

        if not dest:
            dest = os.path.join(self._intf._conn.cache.cache, 'workspace',
                                *self._absuri.strip('/').split('/')[1:])
            
        if not os.path.exists(os.path.dirname(dest)):
            os.makedirs(os.path.dirname(dest))

        # FIXME: with the current .get() implementation if a file was
        # previously dl with a custom location it will be moved back
        # to the default and copied to the custom location of this function
        src = self.get()

        if src != dest:
            shutil.copy2(src, dest)
            
        return dest

    def put(self, src, format='U', content='U', tags='U', **datatypes):
        """ Uploads a file to XNAT.

            Parameters
            ----------
            src: string
                Location of the local file to upload.
            format: string   
                Optional parameter to specify the file format. 
                Defaults to 'U'.
            content: string
                Optional parameter to specify the file content. 
                Defaults to 'U'.
            tags: string
                Optional parameter to specify tags for the file. 
                Defaults to 'U'.
        """

        format = "'%s'" % format if ' ' in format else format
        content = "'%s'" % content if ' ' in content else content
        tags = "'%s'" % tags if ' ' in tags else tags

        put_uri = "%s?format=%s&content=%s&tags=%s" % \
            (self._uri, format, content, tags)

        BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
        CRLF = '\r\n'
        L = []
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; '
                 'name="%s"; filename="%s"' % (os.path.basename(src), src)
                 )
        L.append('Content-Type: %s' % 
                 mimetypes.guess_type(src)[0] or 'application/octet-stream')
        L.append('')
        L.append(open(src, 'rb').read())
        L.append('--' + BOUNDARY + '--')
        L.append('')
        body = CRLF.join(L)
        content_type = 'multipart/form-data; boundary=%s' % BOUNDARY

        guri = uri_grandparent(self._uri)

        if not self._intf.select(guri).exists():
            self._intf.select(guri).create(**datatypes)

        self._intf._exec(self._uri, 'PUT', body, 
                         headers={'content-type':content_type})

    insert = put
    create = put

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

    def labels(self):
        """ Gets the file labels.
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

        return '%s//%s:%s@%s%s' % (self._intf._server.split('//')[0],
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
        return Subjects([eobj for eobj in self
                         if set(projects).issubset(eobj.shares().get())
                         ], 
                        self._intf
                        )

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)

class Experiments(CObject):
    __metaclass__ = CollectionType

    def sharing(self, projects=[]):
        return Experiments([eobj for eobj in self
                            if set(projects).issubset(eobj.shares().get())
                            ], 
                           self._intf
                           )

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)

class Assessors(CObject):
    __metaclass__ = CollectionType

    def sharing(self, projects=[]):
        return Assessors([eobj for eobj in self
                          if set(projects).issubset(eobj.shares().get())
                          ], 
                         self._intf
                         )

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

