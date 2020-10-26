import lxml
import os
import os.path as op
import sys
import re
import shutil
import tempfile
import zipfile
# import time
import codecs
from fnmatch import fnmatch
from itertools import islice
from lxml import etree
from pathlib import Path


from .uriutil import join_uri, translate_uri, uri_segment
from .uriutil import uri_last, uri_nextlast
from .uriutil import uri_parent, uri_grandparent
from .uriutil import uri_shape
from .uriutil import file_path
from .jsonutil import JsonTable, get_selection
from .pathutil import find_files, ensure_dir_exists
from .attributes import EAttrs
from .search import rpn_contraints, query_from_xml
from .errors import is_xnat_error, parse_put_error_message
from .errors import DataError, ProgrammingError, catch_error
from .provenance import Provenance
# from .pipelines import Pipelines
from . import schema
from . import httputil
from . import downloadutils
from . import derivatives
import types
import pkgutil
import inspect
import six
from six import string_types, add_metaclass
if six.PY2:
    from urllib import quote, unquote  # Python 2.X
elif six.PY3:
    from urllib.parse import quote, unquote
    unicode = str

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
                                   self._intf)
                           for eobj in self],
                          self._intf)
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

        rsc_name = name.lower() + 's' \
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
        rsc_name = name.lower() + 's' \
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
def __get_modules__(m):
    modules = []
    prefix = m.__name__ + '.'
    for importer, modname, ispkg in pkgutil.iter_modules(m.__path__, prefix):
        module = __import__(modname, fromlist='dummy')
        if not ispkg:
            modules.append(module)
        else:
            modules.extend(__get_modules__(module))
    return modules


def __find_all_functions__(m):
    functions = {}
    modules = __get_modules__(m)
    for m in modules:
        for name, obj in inspect.getmembers(m):
            if inspect.isfunction(obj):
                functions.setdefault(m, []).append(obj)
    return functions


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

        self._uri = quote(translate_uri(uri))
        self._urn = unquote(uri_last(self._uri))
        self._urt = uri_nextlast(self._uri)
        self._intf = interface
        self.attrs = EAttrs(self)

        functions = __find_all_functions__(derivatives)

        for m, mod_functions in functions.items():
            is_resource = False
            if (hasattr(m, 'XNAT_RESOURCE_NAME') and
                    self._urn == m.XNAT_RESOURCE_NAME) or \
                    (hasattr(m, 'XNAT_RESOURCE_NAMES') and
                        self._urn in m.XNAT_RESOURCE_NAMES):
                is_resource = True

            if is_resource:
                for f in mod_functions:
                    setattr(self, f.__name__, types.MethodType(f, self))

    def __getstate__(self):
        return {'uri': self._uri,
                'interface': self._intf}

    def __setstate__(self, dict):
        self.__init__(dict['uri'], dict['interface'])

    def __repr__(self):
        return '<%s Object> %s' % (self.__class__.__name__,
                                   unquote(uri_last(self._uri)))

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
                       if col not in schema.json[self._urt]
                       or col != 'URI'] + schema.json[self._urt])
        get_id = p_uri + '?format=json&columns=%s' % ','.join(columns)

        for pattern in self._intf._struct.keys():
            if fnmatch(uri_segment(
                    self._uri.split(
                        self._intf._get_entry_point(), 1)[1], -2), pattern):

                reg_pat = self._intf._struct[pattern]
                filters.setdefault('xsiType', set()).add(reg_pat)

        if filters:
            get_id += '&' + \
                '&'.join('%s=%s' % (item[0], item[1])
                         if isinstance(item[1], string_types)
                         else '%s=%s' % (item[0],
                                         ','.join([val for val in item[1]]))
                         for item in filters.items())

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
            return self.id() is not None
        except Exception as e:
            if DEBUG:
                print(e)
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

                   - `element.create(ID='theid')`
                   - `subject.create(**{'xnat:subjectData/ID':'theid'})`


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

                - To give the ID the same value as the label use
                  use_label=True e.g element.create(use_label=True)

            Examples
            --------

                >>> interface.select('/project/PROJECT/subject'
                                     '/SUBJECT/experiment/EXP/scan/SCAN'
                            ).create(experiments='xnat:mrSessionData',
                                     scans='xnat:mrScanData'
                                     )

            See Also
            --------
            :func:`EObject.id`
            :func:`EObject.label`
            :func:`EObject.datatype`
        """
        if 'xml' in params and op.exists(params.get('xml')):

            f = codecs.open(params.get('xml'))
            doc = f.read()
            f.close()

            try:
                doc_tree = etree.fromstring(doc)
                doc_tree.xpath('//*')[0].set('label', uri_last(self._uri))
                doc = etree.tostring(doc_tree)
            except Exception:
                pass

            body, content_type = httputil.file_message(
                doc.decode(), 'text/xml', 'data.xml', 'data.xml')

            _uri = self._uri
            if ('allowDataDeletion' in params and
                    params.get('allowDataDeletion') is False):
                _uri += '?allowDataDeletion=false'
            else:
                _uri += '?allowDataDeletion=true'

            self._intf._exec(_uri,
                             method='PUT',
                             body=body,
                             headers={'content-type': content_type})

            return self

        datatype = params.get(uri_nextlast(self._uri))
        struct = self._intf._struct

        if datatype is None:
            for uri_pattern in struct.keys():
                if fnmatch(
                    self._uri.split(
                        self._intf._get_entry_point(), 1)[1], uri_pattern):
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
                 if param not in schema.resources_types + ['use_label']
                    and (param.startswith(datatype) or '/' not in param)
                 ]

            create_uri = '%s?xsiType=%s' % (self._uri, datatype)

            if 'ID' not in local_params \
                    and '%s/ID' % datatype not in local_params \
                    and params.get('use_label'):

                create_uri += '&%s/ID=%s' % (datatype, uri_last(self._uri))

            if local_params:
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
                print('CREATE', parent_element, parent_datatype)
            parent_element.create(**params)

        if DEBUG:
            print('PUT', create_uri)

        if 'params' in params and 'event_reason' in params['params']:
            if DEBUG:
                print('Found event_reason')
            output = self._intf._exec(create_uri, 'PUT', **params)
        else:
            if DEBUG:
                print('event_reason not found')
            output = self._intf._exec(create_uri, 'PUT')

        if is_xnat_error(output):
            paths = []
            for datatype_name, element_name \
                    in parse_put_error_message(output):

                path = self._intf.inspect.schemas.look_for(
                    element_name, datatype_name)

                paths.extend(path)

                if DEBUG:
                    print(path, 'is required')

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

        out = self._intf._exec(delete_uri, 'DELETE')

        if is_xnat_error(out):
            catch_error(out)

    def get(self):
        """ Retrieves the XML document corresponding to this element.
        """
        return self._intf._exec(self._uri + '?format=xml', 'GET')

    def xpath(self, xpath):
        root = etree.fromstring(self.get())

        return root.xpath(xpath, namespaces=root.nsmap)

    def namespaces(self):
        pass

    def parent(self):
        uri = uri_grandparent(self._uri)
        klass = uri_nextlast(uri).title().rsplit('s', 1)[0]
        if klass:
            Klass = globals()[klass]
            return Klass(uri, self._intf)
        else:
            return None

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
        if not tag.references().get():
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

        if isinstance(cbase, string_types):
            self._ctype = 'cobjectcuri'
        elif isinstance(cbase, CObject):
            self._ctype = 'cobjectcobject'
        elif isinstance(cbase, list) and cbase:
            if isinstance(cbase[0], string_types):
                self._ctype = 'cobjecteuris'
            if isinstance(cbase[0], EObject):
                self._ctype = 'cobjecteobjects'
            if isinstance(cbase[0], CObject):
                self._ctype = 'cobjectcobjects'
        elif isinstance(cbase, list) and not cbase:
            self._ctype = 'cobjectempty'
        else:
            raise Exception('Invalid collection accessor type: %s' % cbase)

    def __repr__(self):
        return '<Collection Object> %s' % id(self)

    def _call(self, columns):
        try:
            uri = translate_uri(self._cbase)
            uri = quote(uri)

            # request_shape = uri_shape(
            #    '%s/0' % uri.split(self._intf._get_entry_point(), 1)[1])

            # gather = uri.split('/')[-1] in ['experiments', 'assessors',
            #                                'scans', 'reconstructions']

            # tick = time.gmtime(time.time())[5] % \
            #    self._intf.inspect._tick == 0 and\
            #    self._intf.inspect._auto

            columns += ['xsiType']

            query_string = '?format=json&columns=%s' % ','.join(columns)

            if self._filters:
                query_string += '&' + '&'.join(
                    '%s=%s' % (item[0], item[1])
                    if isinstance(item[1], (str, unicode))
                    else '%s=%s' % (
                        item[0], ','.join([val for val in item[1]]))
                    for item in self._filters.items()
                    )

            if DEBUG:
                print(uri + query_string)
            jtable = self._intf._get_json(uri + query_string)

            _type = uri.split('/')[-1]
            self._learn_from_table(_type, jtable, None)

            return jtable
        except Exception as e:
            if DEBUG:
                raise e
            return []

    def _learn_from_table(self, _type, jtable, reqcache):
        request_knowledge = {}

        for element in jtable:
            xsitype = element.get('xsiType')
            if xsitype:
                # Only some of the xnat elements return xsiType like we asked
                # them to.Projects and Subjects are two known offenders so we
                #  cannot update our knowledge of them.
                uri = element.get('URI').split(self._intf._get_entry_point(),
                                               1)[1]
                uri = uri.replace(uri.split('/')[-2], _type)
                shape = uri_shape(uri)
                request_knowledge[shape] = xsitype

        self._intf._struct.update(request_knowledge)

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
                    eid = unquote(res[id_header])
                    if fnmatch(eid, self._pattern):
                        klass_name = uri_last(self._cbase
                                              ).rstrip('s').title()
                        Klass = globals().get(klass_name, self._intf.__class__)
                        eobj = Klass(join_uri(self._cbase, eid), self._intf)
                        if self._nested is None:
                            self._run_callback(self, eobj)
                            yield eobj
                        else:
                            Klass = globals().get(self._nested.title(),
                                                  self._intf.__class__)
                            for subeobj in Klass(
                                    cbase=join_uri(eobj._uri, self._nested),
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
                    title = uri_nextlast(uri).rstrip('s').title()
                    Klass = globals().get(title, self._intf.__class__)
                    eobj = Klass(uri, self._intf)
                    if self._nested is None:
                        self._run_callback(self, eobj)
                        yield eobj
                    else:
                        Klass = globals().get(self._nested.title(),
                                              self._intf.__class__)
                        for subeobj in Klass(
                                cbase=join_uri(eobj._uri, self._nested),
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
                        Klass = globals().get(self._nested.rstrip('s').title(),
                                              self._intf.__class__)
                        for subeobj in Klass(
                                cbase=join_uri(eobj._uri, self._nested),
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
                        Klass = globals().get(self._nested.title(),
                                              self._intf.__class__)
                        for subeobj in Klass(
                                cbase=join_uri(eobj._uri, self._nested),
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
                            Klass = globals().get(cobj._nested.title(),
                                                  self._intf.__class__)

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

    def __getitem__(self, k):
        """ Use itertools.islice() to support indexed access and slicing.
        """
        if isinstance(k, slice):
            return islice(self, k.start, k.stop, k.step)
        else:
            return next(islice(self, k, k+1))

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
        if not args:
            return [unquote(uri_last(eobj._uri)) for eobj in self]
        else:
            entries = []

            for eobj in self:
                entry = ()
                for arg in args:
                    if arg == 'id':
                        self._id_header = 'ID'
                        entry += (unquote(uri_last(eobj._uri)),)
                    elif arg == 'label':
                        self._id_header = 'label'
                        entry += (unquote(uri_last(eobj._uri)),)
                    else:
                        entry += (eobj,)

                entries.append(entry)

            if len(args) != 1:
                return entries
            else:
                return [e[0] for e in entries]

    fetchall = get

    def __nonzero__(self):
        try:
            self.__iter__().next()
        except StopIteration:
            return False
        else:
            return True

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
        if not tag.references().get():
            tag.delete()

    def where(self, constraints=None, template=None, query=None):
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
            :func:`search.Search`
        """

        if isinstance(constraints, (str, unicode)):
            constraints = rpn_contraints(constraints)
        elif isinstance(template, (tuple)):
            tmp_bundle = self._intf.manage.search.get_template(
                template[0], True)
            tmp_bundle = tmp_bundle % template[1]
            constraints = query_from_xml(tmp_bundle)['constraints']
        elif isinstance(query, (str, unicode)):
            tmp_bundle = self._intf.manage.search.get(query, 'xml')
            constraints = query_from_xml(tmp_bundle)['constraints']
        elif isinstance(constraints, list):
            pass
        else:
            raise ProgrammingError('One in [contraints, template and '
                                   'query] parameters must be correctly '
                                   'set.'
                                   )

        # _columns = [
        #     'xnat:subjectData/PROJECT',
        #     'xnat:subjectData/SUBJECT_ID',
        #     ] + ['%s/ID' %qtype for qtype in _queried_types]

        # bundle = build_search_document(
        #     'xnat:imageSessionData', _columns, constraints)

        # content = self._intf._exec(
        #     "%s/search?format=json" % self._intf._entry,
        #     'POST', bundle)

        # if content.startswith('<html>'):
        #     raise Exception(content.split('<h3>')[1].split('</h3>')[0])

        # results = JsonTable(json.loads(content)['ResultSet']['Result'])

        # return results

        results = query_with(
            interface=self._intf,
            join_field='xnat:subjectData/SUBJECT_ID',
            common_field='SUBJECT_ID',
            return_values=['xnat:subjectData/PROJECT',
                           'xnat:subjectData/SUBJECT_ID'],
            _filter=constraints
            )

        searchpop = ['%s/projects/' % self._intf._get_entry_point() +
                     '%(project)s/subjects/%(subject_id)s' % res
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
            poi = set(searchpop).intersection([eobj._uri for eobj in cobj])
        else:
            poi = searchpop

        cobj._cbase = list(poi)
        cobj._ctype = 'cobjecteuris'
        cobj._nested = None
        cobj._id_header = backup_header

        return self

# specialized classes


@add_metaclass(ElementType)
class Project(EObject):

    def __init__(self, uri, interface):
        """
            Parameters
            ----------
            uri: string
                The file resource URI
            interface: Interface Object
        """

        EObject.__init__(self, uri, interface)
        # self.pipelines = Pipelines(self.id(), self._intf)

    def __repr__(self):
        interface = self._intf

        # Check if project exists
        if self.exists():
            project_id = self.id()

            data = interface.select('xnat:projectData').all().data
            data = [e for e in data if e['id'] == project_id][0]

            # Collecting project details
            name = data['name']

            n_subjects = len(list(self.subjects()))

            # Creating the project url
            url = interface._server + self._uri + '?format=html'

            # Listing experiments
            exp = []
            for e in ['mr', 'ct', 'pet', 'ut']:
                field = 'proj_%s_count' % e
                if data[field]:
                    item = '{f} {e} experiment{s}'
                    final_s = {True: 's', False: ''}[int(data[field]) > 1]
                    item = item.format(f=data[field],
                                       e=e.upper(),
                                       s=final_s)
                    exp.append(item)

            owners = [e.strip(' ')
                      for e in data['project_owners'].split(' <br/> ')]
            # Creating the output string to be returned
            output = '<{cl} Object> {id} `{label}` ({access}) {n_subjects}'\
                ' subject{s} {exp} (owner: {owner}) (created on {insert_date}'\
                ') {url}'
            output = output.format(cl=self.__class__.__name__,
                                   id=project_id,
                                   label=name,
                                   s={True: 's', False: ''}[n_subjects > 1],
                                   n_subjects=n_subjects,
                                   owner='/'.join(owners),
                                   insert_date=data['insert_date'],
                                   access=data['project_access'],
                                   url=url,
                                   exp=' '.join(exp))

            return output
        else:
            return '<%s Object> %s' % (self.__class__.__name__,
                                       self._urn)

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
        j = JsonTable(self._intf._get_json(join_uri(self._uri, 'users')))
        return ''.join(j.where(login=login)['displayname']).lower().rstrip('s')

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
                                  self.user_role(login).title() + 's',
                                  login
                                  ),
                         'DELETE')

    def datatype(self):
        return 'xnat:projectData'

    def experiments(self, id_filter='*'):
        datapath = '%s/projects/%s/experiments'
        dp = datapath % (self._intf._get_entry_point(), self.id())
        return Experiments(dp, self._intf, id_filter)

    def experiment(self, ID):
        datapath = '%s/projects/%s/experiments/%s'
        dp = datapath % (self._intf._get_entry_point(), self.id(), ID)

        tmp = Experiment(dp, self._intf)
        if tmp.id() == ID:
            return tmp
        else:
            # if id id not mach given id (which may have been a label
            # re-select with the ID of the matching experiment.
            return Experiment(datapath % (
                self._intf._get_entry_point(), self.id(), tmp.id()),
                self._intf
                )

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

    def add_custom_variables(self, custom_variables,
                             allow_data_deletion=False):
        """Adds a custom variable to a specified group

        Parameters
        ----------

        custom_variables: a dictionary
        allow_data_deletion : a boolean

        Examples
        --------

        >>> variables = {'Subjects' : {'newgroup' : {'foo' : 'string',
            'bar': 'int'}}}
        >>> project.add_custom_variables(variables)

        """
        tree = lxml.etree.fromstring(self.get())

        update = False

        for protocol, value in custom_variables.items():
            try:
                protocol_element = tree.xpath(
                    "//xnat:studyProtocol[@name='%s']" % protocol,
                    namespaces=tree.nsmap).pop()

            except IndexError:
                raise ValueError(
                    'Protocol %s not in current schema' % protocol
                    )

            try:
                definitions_element = protocol_element.xpath(
                    'xnat:definitions', namespaces=tree.nsmap).pop()
            except IndexError:
                update = True
                definitions_element = lxml.etree.Element(
                    lxml.etree.QName(tree.nsmap['xnat'], 'definitions'),
                    nsmap=tree.nsmap
                    )
                protocol_element.append(definitions_element)

            for group, fields in value.items():
                try:
                    group_element = definitions_element.xpath(
                        "xnat:definition[@ID='%s']" % group,
                        namespaces=tree.nsmap).pop()

                    fields_element = group_element.xpath(
                        "xnat:fields",
                        namespaces=tree.nsmap).pop()

                except IndexError:
                    update = True

                    group_element = lxml.etree.Element(
                        lxml.etree.QName(tree.nsmap['xnat'], 'definition'),
                        nsmap=tree.nsmap
                        )
                    group_element.set('ID', group)
                    group_element.set(
                        'data-type', protocol_element.get('data-type'))
                    group_element.set('description', '')
                    group_element.set('project-specific', '1')
                    definitions_element.append(group_element)
                    fields_element = lxml.etree.Element(
                        lxml.etree.QName(tree.nsmap['xnat'], 'fields'),
                        nsmap=tree.nsmap
                        )
                    group_element.append(fields_element)

                for field, datatype in fields.items():
                    try:
                        field_element = fields_element.xpath(
                            "xnat:field[@name='%s']" % field,
                            namespaces=tree.nsmap).pop()
                    except IndexError:
                        field_element = lxml.etree.Element(
                            lxml.etree.QName(tree.nsmap['xnat'], 'field'),
                            nsmap=tree.nsmap)
                        field_element.set('name', field)
                        field_element.set('datatype', datatype)
                        field_element.set('type', 'custom')
                        field_element.set('required', '0')
                        field_element.set(
                            'xmlPath',
                            "xnat:%s/fields/field[name=%s]/field" % (
                                protocol_element.get(
                                    'data-type').split(':')[-1], field)
                            )
                        fields_element.append(field_element)
                        update = True
        if update:
            body, content_type = httputil.file_message(
                lxml.etree.tostring(tree).decode('utf-8'),
                'text/xml',
                'cust.xml',
                'cust.xml'
                )

            uri = self._uri
            if allow_data_deletion:
                uri = self._uri + '?allowDataDeletion=true'
            self._intf._exec(uri, method='PUT', body=str(body),
                             headers={'content-type': content_type})

    def get_custom_variables(self):
        """Retrieves custom variables as a dictionary

        It has the format {studyProtocol: { setname : {field: type, ...}}}

        """
        tree = lxml.etree.fromstring(self.get())
        nsmap = tree.nsmap
        custom_variables = {}
        for studyprotocols in tree.xpath('//xnat:studyProtocol',
                                         namespaces=nsmap):

            protocol_name = studyprotocols.get('name')
            custom_variables[protocol_name] = {}

            for definition in studyprotocols.xpath(('xnat:definitions'
                                                    '/xnat:definition'),
                                                   namespaces=nsmap):

                definition_id = definition.get('ID')
                custom_variables[protocol_name][definition_id] = {}
                for field in definition.xpath('xnat:fields/xnat:field',
                                              namespaces=nsmap):

                    field_name = field.get('name')
                    if field.get('type') == 'custom':
                        custom_variables[protocol_name][definition_id][
                            field_name] = field.get('datatype')

        return custom_variables

    def aliases(self):
        """Returns the aliases for this project.

           Returns
           -------
           List of aliases
        """

        uri = '/data/projects'
        options = {'columns': 'alias', 'format': 'csv'}
        data = self._intf.get(uri, params=options).text
        from .jsonutil import csv_to_json
        data = csv_to_json(data)

        # parse the results
        return [item['alias'] for item in data
                if item['alias'] and item['ID'] == self._urn]

    def description(self):
        """Returns the description for this project.

        Returns
        -------
        Description (string) of the project.
        """
        return self.attrs.get('description')


@add_metaclass(ElementType)
class Subject(EObject):

    def datatype(self):
        return 'xnat:subjectData'

    def __repr__(self):
        interface = self._intf

        # Check if subject exists
        if self.exists():
            subject_id = self.id()
            columns = ['xnat:subjectData/PROJECT',
                       'xnat:subjectData/SUBJECT_ID',
                       'xnat:subjectData/INSERT_DATE',
                       'xnat:subjectData/INSERT_USER',
                       'xnat:subjectData/GENDER_TEXT',
                       'xnat:subjectData/HANDEDNESS_TEXT',
                       'xnat:subjectData/SES',
                       'xnat:subjectData/ADD_IDS',
                       'xnat:subjectData/RACE',
                       'xnat:subjectData/ETHNICITY',
                       'xnat:subjectData/SUBJECT_LABEL']

            dt = 'xnat:subjectData'
            data = interface.select(dt, columns=columns).all().data
            interface._subjectData = data
            data = [e for e in data if e['subject_id'] == subject_id][0]

            # Collecting subject details
            url = interface._server + self._uri + '?format=html'

            project_id = data['project']
            age = self.attrs.get('age')
            gender = data['gender_text']
            handedness = data['handedness_text']
            label = data['subject_label']
            n_expes = len(list(self.experiments()))

            ag = ''
            if [age, gender, handedness] != ['', '', '']:
                ag = []
                if age != '':
                    ag.append('Age: %s' % age)
                if gender != '':
                    ag.append('Gender: %s' % gender)
                if handedness != '':
                    ag.append('Handedness: %s' % handedness)
                ag = '(%s)' % ' - '.join(ag)

            # Creating the output string to be returned
            output = '<{cl} Object> {id} `{label}` (project: {project}) {ag}'\
                ' {n_expes} experiment{final_s} {url}'
            output = output.format(cl=self.__class__.__name__,
                                   label=label,
                                   id=subject_id,
                                   project=project_id,
                                   url=url,
                                   ag=ag,
                                   n_expes=n_expes,
                                   final_s={True: 's', False: ''}[n_expes > 1])

            return output
        else:
            return '<%s Object> %s' % (self.__class__.__name__,
                                       unquote(uri_last(self._uri))
                                       )

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


@add_metaclass(ElementType)
class Experiment(EObject):

    def __init__(self, cbase, interface):
        items = cbase.split('/')
        e = []
        if 'subjects' not in items \
                and 'projects' in items and 'experiments' in items:
            ID = uri_last(cbase)
            e = interface.array.experiments(experiment_id=ID).data

        if len(e) == 1:
            subject_id = e[0]['subject_ID']
            project_id = e[0]['project']

            cbase = '%s/projects/%s/subjects/%s/experiments/%s'
            cbase = cbase % (interface._get_entry_point(),
                             project_id,
                             subject_id,
                             ID)
            return super(Experiment, self).__init__(cbase, interface)

        return super(Experiment, self).__init__(cbase, interface)

    def __repr__(self):
        intf = self._intf

        # Check if experiment exists
        if self.exists():
            eid = self.id()

            e = intf.array.experiments(experiment_id=eid).data[0]
            filter = [('{}/{}'.format(e['xsiType'], 'ID'), '=', eid)]
            data = intf.select(e['xsiType']).where(filter).data[0]

            # Collecting experiment details
            project_id = data['project']
            label = self.label()
            subject_id = data['subject_id']
            e = intf.array.experiments(experiment_id=eid,
                                       columns=['subject_label']).data[0]
            subject_label = e['subject_label']
            insert_date = data['insert_date']
            n_res = len(list(self.resources()))

            n_scans = len(list(self.scans()))

            url = intf._server + self._uri + '?format=html'

            # Creating the output string
            output = '<{cl} Object> {id} `{label}` (subject: {subject_id} '\
                     '`{subject_label}`) (project: {project}) {n_scans} '\
                     'scan{final_s1} {n_res} resource{final_s2} (created on '\
                     '{insert_date}) {url}'

            fs = {True: 's', False: ''}
            output = output.format(cl=self.__class__.__name__,
                                   id=eid,
                                   label=label,
                                   subject_id=subject_id,
                                   subject_label=subject_label,
                                   project=project_id,
                                   url=url,
                                   n_res=n_res,
                                   insert_date=insert_date,
                                   n_scans=n_scans,
                                   final_s1=fs[n_scans > 1],
                                   final_s2=fs[n_res > 1])

            return output
        else:
            return '<%s Object> %s' % (self.__class__.__name__,
                                       unquote(uri_last(self._uri)))

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
        self._intf._exec(self._uri + '?triggerPipelines=true', 'PUT')

    def fix_scan_types(self):
        """ Populate empty scan TYPE attributes based on how similar
            scans were populated.
        """
        self._intf._exec(self._uri + '?fixScanTypes=true', 'PUT')

    def pull_data_from_headers(self):
        """ Pull DICOM header values into the session.
        """
        self._intf._exec(self._uri + '?pullDataFromHeaders=true', 'PUT')

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

            self._intf._exec(self._uri + options, 'PUT', body=[])


@add_metaclass(ElementType)
class Assessor(EObject):

    def __init__(self, uri, interface):
        EObject.__init__(self, uri, interface)

        self.provenance = Provenance(self)

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

    def set_param(self, key, value):
        self.attrs.set('%s/parameters/addParam[name=%s]/addField'
                       % (self.datatype(), key),
                       value
                       )

    def get_param(self, key):
        return self.xpath(
            "//xnat:addParam[@name='%s']/child::text()" % key)[-1]

    def get_params(self):
        return self.xpath("//xnat:addParam/child::text()")[1::2]

    def params(self):
        return self.xpath('//xnat:addParam/attribute::*')


@add_metaclass(ElementType)
class Reconstruction(EObject):

    def __init__(self, uri, interface):
        EObject.__init__(self, uri, interface)

        self.provenance = Provenance(self)

    def datatype(self):
        return (super(Reconstruction, self).datatype()
                or 'xnat:reconstructedImageData'
                )


@add_metaclass(ElementType)
class Scan(EObject):

    def __repr__(self):
        interface = self._intf

        # Check if scan exists
        if self.exists():
            scan_id = self.id()

            # Collect scan details
            attrs = ['ID', 'type', 'frames', 'quality']
            base_url = uri_parent(self._uri)
            scans = self._intf._get_json('{}?columns={}'.format(base_url,
                                                                ','.join(attrs)))
            scan_info = [r for r in scans if r['ID'] == scan_id][0]

            url = interface._server + self._uri + '?format=html'

            # Creating the output string
            output = '<{cl} Object> {id} (`{type}` {n_frames} frames) {quality} {url}'
            output = output.format(cl=self.__class__.__name__,
                                   id=scan_id,
                                   type=scan_info['type'],
                                   n_frames=scan_info['frames'],
                                   quality=scan_info['quality'],
                                   url=url)
            return output
        else:
            return '<%s Object> %s' % (self.__class__.__name__,
                                       unquote(uri_last(self._uri))
                                       )

    def set_param(self, key, value):
        self.attrs.set('%s/parameters/addParam[name=%s]/addField'
                       % (self.datatype(), key),
                       value
                       )

    def get_param(self, key):
        return self.xpath(
            "//xnat:addParam[@name='%s']/child::text()" % key)[-1]

    def get_params(self):
        return self.xpath("//xnat:addParam/child::text()")[1::2]

    def params(self):
        return self.xpath('//xnat:addParam/attribute::*')


@add_metaclass(ElementType)
class Resource(EObject):

    def __repr__(self):

        def sizeof_fmt(num, suffix='B'):
            for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
                if abs(num) < 1024.0:
                    return "%3.2f %s%s" % (num, unit, suffix)
                num /= 1024.0
            return "%.2f %s%s" % (num, 'Y', suffix)

        # Check if resource exists
        if self.exists():
            resource_id = self.id()
            base_url = uri_parent(self._uri)
            resources = self._intf._get_json(base_url)
            res_info = [r for r in resources
                        if r['xnat_abstractresource_id'] == resource_id][0]
            fs = sizeof_fmt(float(res_info['file_size']))

            # Creating the output string
            output = '<{cl} Object> {id} `{label}` ({fc} files {fs})'
            output = output.format(label=self.label(),
                                   cl=self.__class__.__name__,
                                   id=resource_id,
                                   fc=res_info['file_count'],
                                   fs=fs)
            return output
        else:
            return '<%s Object> %s' % (self.__class__.__name__,
                                       unquote(uri_last(self._uri)))

    def get(self, dest_dir, extract=False):
        """ Downloads all the files within a resource.

            ..warning::
                Currently XNAT adds parent folders in the zip file that
                is downloaded to avoid name clashes if several resources
                are downloaded in the same folder. In order to be able to
                download the data uploaded previously with the same
                structure, pyxnat extracts the zip file, removes the extra
                paths and if necessary re-zips it. Careful, it may take
                time, and there is the problem of name clashes.

            Parameters
            ----------
            dest_dir: string
                Destination directory for the resource data.
                if dest_dir is None, then the user's Downloads directory is
                used as the default download location.
            extract: boolean
                If True, the downloaded zip file is extracted.
                If False, not extracted.

            Returns
            -------
            If extract is False, the zip file path.
            If extract is True, the list of file paths previously in
            the zip.
        """
        zip_location = op.join(dest_dir, uri_last(self._uri) + '.zip')

        with open(zip_location, 'wb') as f:
            response = self._intf.get(join_uri(self._uri, 'files') +
                                      '?format=zip', stream=True)
            try:
                count = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        count += 1
                        if count % 10 == 0:
                            # flush the buffer every once in a while.
                            f.flush()
                f.flush()  # and one last flush.
            except Exception as e:
                sys.stderr.write(e)
            finally:
                response.close()

        if DEBUG:
            print(zip_location)

        fzip = zipfile.ZipFile(zip_location, 'r')
        fzip.extractall(path=dest_dir)
        fzip.close()

        members = []
        fzip_namelist = [str(Path(item)) for item in fzip.namelist()]
        for member in fzip_namelist:
            old_path = op.join(dest_dir, member)
            if DEBUG:
                print(member)
                print(member.split('files', 1))
            new_path = op.join(
                dest_dir,
                uri_last(self._uri),
                member.split('files', 1)[1].split(os.sep, 1)[1]
                )

            if not op.exists(op.dirname(new_path)):
                os.makedirs(op.dirname(new_path))

            shutil.move(old_path, new_path)

            members.append(new_path)

        # TODO: cache.delete(...)
        for extracted in fzip_namelist:
            pth = op.join(dest_dir, extracted.split(os.sep, 1)[0])

            if op.isdir(pth):
                shutil.rmtree(pth)

        os.remove(zip_location)

        if not extract:
            fzip = zipfile.ZipFile(zip_location, 'w')
            arcprefix = op.commonprefix(members).rpartition(os.sep)[0]
            arcroot = '/%s' % op.split(arcprefix.rstrip(os.sep))[1]
            for member in members:
                opj = op.join(arcroot, member.split(arcprefix)[1])
                fzip.write(member, opj)
            fzip.close()
            unzippedTree = op.join(dest_dir, uri_last(self._uri))
            if op.exists(unzippedTree):
                if op.isdir(unzippedTree):
                    shutil.rmtree(op.join(dest_dir, uri_last(self._uri)))
                else:
                    os.remove(unzippedTree)

        return zip_location if op.exists(zip_location) else members

    def put(self, sources, overwrite=False, extract=True, **datatypes):
        """ Insert a list of files in a single resource element.

            This method takes all the files an creates a zip with them
            which will be the element to be uploaded and then extracted on
            the server.
            If the files have a common prefix directory, that directory name
            will be used.  If not, then "files" will be used as the zip name.

            If avaiable, compression will be used on the zip file.

            Parameters
            ----------
            sources: List of paths of files to upload.

            overwrite: boolean
                If True, overwrite the files that already exist under the
                    given id.
                If False, do not overwrite (Default)

            extract: boolean
                If True, the uploaded zip file is extracted. (Default)
                If False, the file is not extracted.

        """
        zip_location = tempfile.mkdtemp(suffix='pyxnat')

        # get the largest common directory.
        arcprefix, _, _ = op.commonprefix(sources).rpartition(op.sep)
        # get just the name of the largest common directory.
        zip_name = op.split(arcprefix.rstrip(op.sep))[1]
        arcroot = '/%s' % zip_name

        if not zip_name:
            # if no common prefix, then use "files" as the zip file name.
            # inside, each file will be directly under the zip root.
            zip_name = "files"

        zip_name = op.join(zip_location, zip_name + ".zip")
        fzip = None
        try:
            # use compression if avaiable.
            fzip = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
        except RuntimeError:
            print("Zip compression not supported for uploading files.")
            fzip = zipfile.ZipFile(zip_name, 'w')

        for src in sources:
            fzip.write(src, op.join(arcroot, src.split(arcprefix)[1]))

        fzip.close()

        self.put_zip(zip_name, overwrite=overwrite, extract=extract,
                     **datatypes)
        os.remove(zip_name)
        os.rmdir(zip_location)

    def put_zip(self, zip_location, overwrite=False, extract=True,
                **datatypes):
        """ Uploads a zip or tgz file an then extracts it on the server.

            After the compressed file is extracted the individual
            files are accessible separately, or as a whole using get_zip.

            Parameters
            ----------
            zip_location: Path to zip file for upload.

            overwrite: boolean
                If True, overwrite the files that already exist under the
                    given id.
                If False, do not overwrite (Default)

            extract: boolean
                If True, the uploaded zip file is extracted. (Default)
                If False, the file is not extracted.
        """
        if not self.exists():
            self.create(**datatypes)

        if extract:
            do_extract = '?extract=true'
        else:
            do_extract = ''

        self.file(op.split(zip_location)[1] + do_extract
                  ).put(zip_location, overwrite=overwrite, **datatypes)

    def put_dir(self, src_dir, overwrite=False, extract=True, **datatypes):
        """ Finds recursively all the files in a folder and uploads
            them using `insert`. Uses put_zip internally.

            Parameters
            ----------
            src_dir: Path to directory to upload.

            overwrite: boolean
                If True, overwrite the files that already exist under the
                    given id.
                If False, do not overwrite (Default)

            extract: boolean
                If True, the uploaded zip file is extracted. (Default)
                If False, the file is not extracted.
        """
        self.put(find_files(src_dir), overwrite=overwrite, extract=extract,
                 **datatypes)

    batch_insert = put
    zip_insert = put_zip
    dir_insert = put_dir

    def datatype(self):
        return (super(Resource, self).datatype()
                or 'xnat:abstractResource'
                )

    def attributes(self):
        """ Files attributes include:
                - URI
                - Name
                - Size in bytes
                - path (relative to the parent resource)
                - tags
                - format
                - content
            Returns
            -------
            dict : a dictionary with the resource attributes
        """

        return self._getcells(['URI', 'Name', 'Size', 'path',
                               'tags', 'format', 'content'])


class In_Resource(Resource):

    def parent(self):
        uri = uri_grandparent(self._uri)
        Klass = globals()[uri.split('/')[-3].title().rsplit('s', 1)[0]]
        return Klass(uri_parent(uri), self._intf)


@add_metaclass(ElementType)
class Out_Resource(Resource):

    def parent(self):
        uri = uri_grandparent(self._uri)
        Klass = globals()[uri.split('/')[-3].title().rsplit('s', 1)[0]]
        return Klass(uri_parent(uri), self._intf)


@add_metaclass(ElementType)
class File(EObject):
    """ EObject for files stored in XNAT.
    """

    def __init__(self, uri, interface):
        """
            Parameters
            ----------
            uri: string
                The file resource URI
            interface: Interface Object
        """

        EObject.__init__(self, uri, interface)
        self._urn = file_path(uri)
        self._absuri = None

    def __repr__(self):
        return '<%s Object> %s' % (self.__class__.__name__,
                                   self._urn)

    def attributes(self):
        """ Files attributes include:
                - URI
                - Name
                - Size in bytes
                - path (relative to the parent resource)
                - file_tags
                - file_format
                - file_content

            Returns
            -------
            dict : a dictionary with the file attributes
        """

        return self._getcells(['URI', 'Name', 'Size', 'path',
                               'file_tags', 'file_format', 'file_content'])

    def get(self, dest=None):
        """ Downloads the file.

            Parameters
            ----------
            dest: string | None

                - If dest is None, then the user's Downloads directory is used
                    as the default download location.
                - Else the file is downloaded at the requested location.
                    Path should include the file name.
                    eg: /path/to/file.txt

            Returns
            -------
            string : the file location.
        """
        if not self._absuri:
            self._absuri = self._getcell('URI')

        if self._absuri is None:
            raise DataError('Cannot get file: does not exists')

        if not dest:
            dest = op.join(op.expanduser("~"), 'Downloads', self.id())
            if not ensure_dir_exists(op.dirname(dest)):
                if DEBUG:
                    print("File.get: failed to create dir")
                raise DataError('Cannot create dir for file: %s' % (dest))

        if DEBUG:
            print(("get_file:", dest))

        with open(dest, 'wb') as f:
            response = self._intf.get(self._uri, stream=True)
            try:
                count = 0
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        count += 1
                        if count % 10 == 0:
                            # flush the buffer every once in a while.
                            f.flush()
                f.flush()  # and one last flush.
            except Exception as e:
                sys.stderr.write(e)
            finally:
                response.close()
        return dest

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

        return self.get(dest)

    def put(self, src, format='U', content='U', tags='U', overwrite=False,
            **datatypes):
        """ Uploads a file to XNAT.

            Parameters
            ----------
            src: string
                Location of the local file to upload or the actual content
                to upload.
            format: string
                Optional parameter to specify the file format.
                Defaults to 'U'.
            content: string
                Optional parameter to specify the file content.
                Defaults to 'U'.
            tags: string
                Optional parameter to specify tags for the file.
                Defaults to 'U'.
            overwrite: boolean
                Optional parameter to specify if the file should be
                overwritten. Defaults to False.
        """

        # First make sure parents and grandparents exist.

        # URI is in the form of data/.../something/files/me so
        # guri = data/.../something
        guri = uri_grandparent(self._uri)

        if not self._intf.select(guri).exists():
            self._intf.select(guri).insert(**datatypes)

        resource_id = self._intf.select(guri).id()
        isFile = False

        # Cleanup the src and make sure it exists.
        try:
            if op.exists(src):
                isFile = True
                # path = src
                # name = op.basename(path).split('?')[0]
            # else:
                # path = self._uri.split('/')[-1]
                # name = path
        except Exception:
            pass  # FIXME
            # path = self._uri.split('/')[-1]
            # name = path

        self._absuri = unquote(
            re.sub('resources/.*?/',
                   'resources/%s/' % resource_id, self._uri)
            )

        query_args = {
            'format': format,
            'content': content,
            'tags': tags,
            'overwrite': 'true' if overwrite else 'false',
            'inbody': 'true'
            }

        if 'params' in datatypes:
            query_args.update(datatypes['params'])
            # Pass on params such as event_reason

        if '?' in self._absuri:
            k, v = self._absuri.split('?')[1].split('=')
            query_args[k] = v
            self._absuri = self._absuri.split('?')[0]

        if DEBUG:
            print(('INSERT FILE', op.exists(src)))
            print("URI is: " + self._absuri)

        response = None
        if isFile:
            # If src was a file, use inbody streaming to send the file
            with open(src, 'rb') as f:
                response = self._intf.post(self._absuri, params=query_args,
                                           data=f)
        else:
            # If it wasn't a file we can just dump the src as data directly.
            response = self._intf.post(self._absuri, params=query_args,
                                       data=src)

        # default error handling.
        if (response is not None and not response.ok) or \
           is_xnat_error(response.content):
            if DEBUG:
                print(response.keys())
                print(response.get("status"))
            msg = '''pyxnat.file.put failure:
                        URI: {response.url}
                        status code: {response.status_code}
                        headers: {response.headers}
                        content: {response.content}
                    '''.format(response=response)
            catch_error(response.content, msg)

    insert = put
    create = put

    def delete(self):
        """ Deletes the file on the server.
        """
        if not self._absuri:
            self._absuri = self._getcell('URI')

        if self._absuri is None:
            raise DataError('Cannot delete file: does not exists')

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

    def last_modified(self):
        """ Gets the file last-modified date.
        """

        if not self._absuri:
            self._absuri = self._getcell('URI')

        if self._absuri is None:
            raise DataError('Cannot get file: does not exists')

        info = self._intf._get_head(self._absuri)
        return info['last-modified']


@add_metaclass(ElementType)
class In_File(File):
    pass


@add_metaclass(ElementType)
class Out_File(File):
    pass


@add_metaclass(CollectionType)
class Projects(CObject):
    pass


@add_metaclass(CollectionType)
class Subjects(CObject):

    def sharing(self, projects=[]):
        return Subjects([eobj for eobj in self
                         if set(projects).issubset(eobj.shares().get())],
                        self._intf)

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)


@add_metaclass(CollectionType)
class Experiments(CObject):

    def sharing(self, projects=[]):
        return Experiments([eobj for eobj in self
                            if set(projects).issubset(eobj.shares().get())],
                           self._intf)

    def share(self, project):
        for eobj in self:
            eobj.share(project)

    def unshare(self, project):
        for eobj in self:
            eobj.unshare(project)


@add_metaclass(CollectionType)
class Assessors(CObject):

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

    def download(self, dest_dir, type="ALL",
                 name=None, extract=False, safe=False, removeZip=False):
        """
        A wrapper around :func:`downloadutils.download`
        """
        return downloadutils.download(dest_dir, self, type, name,
                                      extract, safe, removeZip)


@add_metaclass(CollectionType)
class Reconstructions(CObject):

    def download(self, dest_dir, type="ALL",
                 name=None, extract=False, safe=False, removeZip=False):
        """
        A wrapper around :func:`downloadutils.download`
        """
        return downloadutils.download(dest_dir, self, type, name,
                                      extract, safe, removeZip)


@add_metaclass(CollectionType)
class Scans(CObject):

    def download(self, dest_dir, type="ALL",
                 name=None, extract=False, safe=False, removeZip=False):
        """
        A wrapper around :func:`downloadutils.download`

        """
        return downloadutils.download(dest_dir, self, type, name,
                                      extract, safe, removeZip)


@add_metaclass(CollectionType)
class Resources(CObject):
    pass


@add_metaclass(CollectionType)
class In_Resources(Resources):
    pass


@add_metaclass(CollectionType)
class Out_Resources(Resources):
    pass


@add_metaclass(CollectionType)
class Files(CObject):
    pass


@add_metaclass(CollectionType)
class In_Files(Files):
    pass


@add_metaclass(CollectionType)
class Out_Files(Files):
    pass

# Utility functions for downloading and extracting zip archives


def _datatypes_from_query(query):
    datatypes = []

    for constraint in query:
        if isinstance(constraint, list):
            datatypes.extend(_datatypes_from_query(constraint))
        elif isinstance(constraint, tuple):
            datatypes.append(constraint[0].split('/')[0])

    return datatypes


def query_with(interface, join_field,
               common_field, return_values, _filter):

    _stm = (join_field.split('/')[0], return_values)
    _cls = rewrite_query(interface, join_field,
                         common_field, _filter)

    return interface.select(*_stm).where(_cls)


def rewrite_query(interface, join_field,
                  common_field, _filter):

    _new_filter = []

    for _f in _filter:
        if isinstance(_f, list):
            _new_filter.append(rewrite_query(
                interface, join_field, common_field, _f))

        elif isinstance(_f, tuple):
            _datatype = _f[0].split('/')[0]
            _res = interface.select(
                _datatype, ['%s/%s' % (_datatype, common_field)]
                ).where([_f, 'AND'])

            _new_f = [(join_field, '=', '%s' % sid)
                      for sid in _res['subject_id']
                      ]

            _new_f.append('OR')
            _new_filter.append(_new_f)

        elif isinstance(_f, (str, unicode)):
            _new_filter.append(_f)

        else:
            raise Exception('Invalid filter')

    return _new_filter
