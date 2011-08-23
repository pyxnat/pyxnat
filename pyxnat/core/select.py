import re

from . import schema
from .search import Search
from .resources import CObject, Project, Projects # imports used implicitly
from .uriutil import inv_translate_uri, check_entry
# from .uriutil import uri_last
from .errors import ProgrammingError

DEBUG = False

def is_type_level(element):
    return element.strip('/') in schema.resources_types and \
           not is_expand_level(element)

def is_singular_type_level(element):
    return element.strip('/') in schema.resources_singular and \
           not is_expand_level(element)

def is_expand_level(element):
    return element.startswith('//') and \
        element.strip('/') in schema.resources_types

def is_id_level(element):
    return element is not None and \
        element.strip('/') not in schema.resources_types

def is_wildid_level(element):
    return element is not None and \
        element.strip('/') not in schema.resources_types and \
        ('?' in element or '*' in element)

def expand_level(element, fullpath):

    def find_paths(element, path=[]):
        resources_dict = schema.resources_tree

        element = element.strip('/')
        paths = []

        if path == []:
            path = [element]

        init_path = path[:]

        for key in resources_dict.keys():

            path = init_path[:]
            if element in resources_dict[key]:
                path.append(key)
                look_again = find_paths(key, path)

                if look_again != []:
                    paths.extend(look_again)
                else:
                    path.reverse()
                    paths.append('/' + '/'.join(path))

        return paths

    absolute_paths = find_paths(element)

    els = re.findall('/{1,2}.*?(?=/{1,2}|$)', fullpath)

    index = els.index(element)

    if index == 0:
        return absolute_paths
    else:
        for i in range(1, 4):
            if is_type_level(els[index - i]) or is_expand_level(els[index - i]):
                parent_level = els[index - i]
                break

    if parent_level.strip('/') in schema.resources_singular:
        parent_level += 's'

    return [abspath.split(parent_level)[1]
            for abspath in absolute_paths
            if parent_level in abspath]

def mtransform(paths):
    tpaths = []

    for path in paths:
        els = re.findall('/{1,2}.*?(?=/{1,2}|$)', path)
        tels = []
        ignore_path = False

        for i, curr_el in enumerate(els):

            if i + 1 < len(els):
                next_el = els[i + 1]
            else:
                next_el = None

            if is_type_level(curr_el):

                if not is_id_level(next_el):
                    if not is_singular_type_level(curr_el):
                        tels.append(curr_el)
                        tels.append('/*')
                    else:
                        tels.append(curr_el + 's')
                        tels.append('/*')
                else:
                    if not is_singular_type_level(curr_el):
                        if not is_wildid_level(next_el):
                            tels.append(curr_el.rstrip('s'))
                        else:
                            tels.append(curr_el)
                    else:
                        if not is_wildid_level(next_el):
                            tels.append(curr_el)
                        else:
                            tels.append(curr_el + 's')

            elif is_expand_level(curr_el):

                exp_paths = [''.join(els[:i] + [rel_path] + els[i + 1:])
                             for rel_path in expand_level(curr_el, path)
                             ]

                tpaths.extend(mtransform(exp_paths))
                ignore_path = True
                break

            elif is_id_level(curr_el):
                tels.append(curr_el)

            else:
                raise ProgrammingError('in %s' % path)

        if not ignore_path:
            tpaths.append(''.join(tels))

    return tpaths

def group_paths(paths):
    groups = {}

    for path in paths:
        resources = [el
                     for el in re.findall('/{1,2}.*?(?=/{1,2}|$)', path)
                     if el.strip('/') in schema.resources_types \
                         and el.strip('/') not in ['files', 'file']
                     ]

        if len(resources) == 1:
            groups.setdefault(resources[0], set()).add(path)
            continue

        for alt_path in paths:
            if alt_path.endswith(path):

                alt_rsc = \
                    [el for el in re.findall('/{1,2}.*?(?=/{1,2}|$)',
                                             alt_path
                                             )
                     if el.strip('/') in schema.resources_types \
                         and el.strip('/') not in ['files', 'file']
                     ]

                if alt_rsc[-1].strip('/') in \
                        ['files', 'file', 'resources', 'resource'] + \
                        schema.rest_translation.keys():

                    groups.setdefault(alt_rsc[-2] + alt_rsc[-1], set()
                                      ).add(alt_path)

                else:
                    groups.setdefault(alt_rsc[-1], set()).add(alt_path)

    return groups

def compute(path):
    if not re.match('/project(s)?|//.+', path):
        path = '/' + path

    path = inv_translate_uri(path)

    try:
        groups = group_paths(mtransform([path]))
    except:
        raise ProgrammingError('in %s' % path)

    best = []

    for name in groups:
        lightest = (0, None)

        for path in groups[name]:
            score = len(path.split('/'))

            if lightest == (0, None) or lightest[0] > score:
                lightest = (score, path)

        best.append(lightest[1])

    return best


class Select(object):
    """ Data selection interface. Callable object that indicates the
        data to be returned to the user.

        Examples
        --------
            Select with a path:
                >>> interface.select('/projects/myproj/subjects').get()

            Select with a datatype:
                >>> columns = ['xnat:subjectData/PROJECT',
                               'xnat:subjectData/SUBJECT_ID'
                               ]
                >>> criteria = [('xnat:subjectData/SUBJECT_ID', 'LIKE', '*'),
                                'AND'
                                ]
                >>> interface.select('xnat:subjectData', columns
                            ).where(criteria)
    """
    def __init__(self, interface):
        """
            Parameters
            ----------
            interface: :class:`Interface`
                Main interface reference.
        """

        self._intf = interface

    def project(self, ID):
        """ Access a particular project.

            Parameters
            ----------
            ID: string
                ID of the project.
        """
        self._intf._get_entry_point()

        return globals()['Project'](
            '%s/projects/%s' % (self._intf._entry, ID), self._intf)

    def projects(self, id_filter='*'):
        """ Returns the list of all visible projects for the server.

            Parameters
            ----------
            id_filter: string
                Name pattern to filter the returned projects.
        """
        self._intf._get_entry_point()

        return globals()['Projects'](
            '%s/projects' % self._intf._entry, self._intf, id_filter)

    def experiments(self, project_id=None, subject_id=None, subject_label=None
                    , experiment_type='xnat:mrSessionData'
              , columns=None
              , constraints=None
              ):
        """ Returns a list of all visible experiment IDs of the specified type,
            filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_type: string
                xsi path type must be a leaf session type. defaults to 'xnat:mrSessionData'
            columns: List[string]
                list of xsi paths for names of columns to return.
            constraints: list[(tupple)]
                List of tupples for comparison in the form (key, comparison, value)
                valid comparisons are: =, <, <=,>,>=, LIKE
            """

        if columns is None:
            columns = []

        where_clause = []

        if project_id is not None:
            where_clause.append(('%s/project' % experiment_type, "=", project_id))
        if subject_id is not None:
            where_clause.append(('xnat:subjectData/ID', "=", subject_id))
        if subject_label is not None:
            where_clause.append(('xnat:subjectData/LABEL', "=", subject_label))


        if constraints is not None:
            where_clause.extend(constraints)

        if where_clause != []:
            where_clause.append('AND')

        if where_clause != []:
            print where_clause
            table = self.__call__(experiment_type, columns=columns).where(where_clause)
            return table
        else:
            table = self.__call__(experiment_type, columns=columns)
            return table.all()
        pass


    def scans(self, project_id=None, subject_id=None, subject_label=None,
              experiment_id=None, experiment_label=None,
              experiment_type='xnat:imageSessionData',
              scan_type='xnat:imageScanData',
              columns=None,
              constraints=None
              ):

        """ Returns a list of all visible scan IDs of the specified type,
            filtered by optional constraints.

            Parameters
            ----------
            project_id: string
                Name pattern to filter by project ID.
            subject_id: string
                Name pattern to filter by subject ID.
            subject_label: string
                Name pattern to filter by subject ID.
            experiment_id: string
                Name pattern to filter by experiment ID.
            experiment_label: string
                Name pattern to filter by experiment ID.
            experiment_type: string
                xsi path type; e.g. 'xnat:mrSessionData'
            scan_type: string
                xsi path type; e.g. 'xnat:mrScanData', etc.
            constraints: dict
                Dictionary of xsi_type (key--) and parameter (--value)
                pairs by which to filter.
            """

        if constraints is None:
            constraints = {}

        uri = '/data/experiments?xsiType=%s' % experiment_type

        if project_id is not None:
            uri += '&project=%s' % project_id

        if subject_id is not None:
            uri += '&subject_id=%s' % subject_id

        if subject_label is not None:
            uri += '&subject_label=%s' % subject_label

        if experiment_id is not None:
            uri += '&ID=%s' % experiment_id

        if experiment_label is not None:
            uri += '&label=%s' % experiment_label

        uri += '&columns=ID,project,subject_id,%s/ID' % scan_type

        if constraints != {}:
            uri += ',' + ','.join(constraints.keys())

        if columns is not None:
            uri += ',' + ','.join(columns)

        c = {}

        [c.setdefault(key.lower(), value)
         for key, value in constraints.items()
         ]

        return JsonTable(self._intf._get_json(uri)).where(**c)

    def tag(self, name):
        self._intf._get_entry_point()

        return self._intf.manage.tags.get(name).references()

    def tags(self):
        self._intf._get_entry_point()

        return self._intf.manage.tags()

    def __repr__(self):
        return '<Root Object>'

    def __call__(self, datatype_or_path, columns=[]):
        """ Select clause to specify what type of data is to be returned.

            Parameters
            ----------
            datatype_or_path: string
                Can either be a resource path or a datatype:
                    - when a path, REST resources are returned, the
                      `columns` argument is useless.
                    - when a datatype, a search Object is returned,
                      the `columns` argument has to be specified.
            columns: list
                List of fieldtypes e.g. xnat:subjectData/SUBJECT_ID
                Datatype and columns are used to specify the search table
                that has to be returned. Use the method `where` on the
                `Search` object to trigger a search on the database.
        """
        self._intf._get_entry_point()

        if datatype_or_path.startswith('/tag'):
            if len(datatype_or_path.split('/')) == 3:
                return self.tag(datatype_or_path.split('/')[-1])
            else:
                return self.tags()

        if datatype_or_path  in ['/', '//', self._intf._entry]:
            return self

        if datatype_or_path.startswith(self._intf._entry):
            datatype_or_path = datatype_or_path.split(
                self._intf._entry, 1)[1]

        if datatype_or_path.startswith('/'):
            return_list = []

            try:
                for path in compute(datatype_or_path):
                    if DEBUG:
                        print 'path: %s' % path

                    pairs = zip(path.split('/')[1::2], path.split('/')[2::2])

                    # # in case a level id has a / - allowed for files only
                    # if len(path.split('/')[1:]) % 2 == 1 \
                    #         and uri_last(path) not in schema.resources_types:

                    #     pairs[-1] = (pairs[-1][0], uri_last(path))

                    obj = self
                    for resource, identifier in pairs:

                        if isinstance(obj, list):
                            obj = [getattr(sobj, resource)(identifier)
                                   for sobj in obj]
                        else:
                            obj = getattr(obj, resource)(identifier)

                    return_list.append(obj)

                if len(return_list) == 1:
                    return return_list[0]
                else:
                    return CObject(return_list, self._intf)

            except Exception, e:
                if DEBUG:
                    print e
                raise ProgrammingError('in %s' % datatype_or_path)

        else:
            if columns == []:
                columns = self._intf.inspect.datatypes(datatype_or_path)

            return Search(datatype_or_path, columns, self._intf)

