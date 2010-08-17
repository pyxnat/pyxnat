import re

from . import schema
from .search import Search
from .resources import CObject, Projects, Project

DEBUG = False

def is_type_level(element):
    return element.strip('/') in schema.resources_types and \
           not is_expand_level(element)

def is_singular_type_level(element):
    return element.strip('/') in schema.resources_singular and \
           not is_expand_level(element)

def is_expand_level(element):
    return element.startswith('//') and element.strip('/') in schema.resources_types

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
#        for rsc in schema.extra_resources_tree:
#            resources_dict[rsc].extend(schema.extra_resources_tree[rsc])

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
                    paths.append('/'+'/'.join(path))

        return paths

    absolute_paths = find_paths(element)

    els = re.findall('/{1,2}.*?(?=/{1,2}|$)', fullpath)

    index = els.index(element)

    if index == 0:
        return absolute_paths
    else:
        for i in range(1, 4):
            if is_type_level(els[index-i]) or is_expand_level(els[index-i]):
                parent_level = els[index-i]
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

            prev_el = None

            if i+1 < len(els):
                next_el = els[i+1]
            else:
                next_el = None

            if is_type_level(curr_el):

                if not is_id_level(next_el):
                    if not is_singular_type_level(curr_el):
                        tels.append(curr_el)
                        tels.append('/*')
                    else:
                        tels.append(curr_el+'s')
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
                            tels.append(curr_el+'s')        

            elif is_expand_level(curr_el):

                exp_paths = [''.join(els[:i] + [rel_path] + els[i+1:])
                             for rel_path in expand_level(curr_el, path)]

                tpaths.extend(mtransform(exp_paths))
                ignore_path = True
                break

            elif is_id_level(curr_el):
                tels.append(curr_el)

            else:
                raise Exception('Invalid syntax: %s'%path)

        if not ignore_path:
            tpaths.append(''.join(tels))

    return tpaths

def group_paths(paths):
    groups = {}

    for path in paths:
        resources = [el
                     for el in re.findall('/{1,2}.*?(?=/{1,2}|$)', path) 
                     if el.strip('/') in schema.resources_types \
                     and el.strip('/') not in ['files', 'file']]


        if len(resources) == 1:
            groups.setdefault(resources[0], set()).add(path)
            continue

        for alt_path in paths:
            if alt_path.endswith(path):
                alt_rsc = [el
                           for el in re.findall('/{1,2}.*?(?=/{1,2}|$)', alt_path) 
                           if el.strip('/') in schema.resources_types \
                           and el.strip('/') not in ['files', 'file']]
                groups.setdefault(alt_rsc[-2]+alt_rsc[-1], set()).add(alt_path)

    return groups

def compute(path):
    if not re.match('/project(s)?|//.+', path):
        path = '/' + path
 
    try:
        groups = group_paths(mtransform([path]))
    except:
        raise Exception('Invalid syntax: %s'%path)

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
    """ Data selection interface. 
        Callable object that indicates the data to be returned to the user.

        Examples
        --------
            Select with a path:
                >>> interface.select('/projects/myproj/subjects').get()

            Select with a datatype:
                >>> interface.select('xnat:subjectData', ['xnat:subjectData/PROJECT', 'xnat:subjectData/SUBJECT_ID']
                            ).where([('xnat:subjectData/SUBJECT_ID', 'LIKE', '*'), 'AND'])
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
        return globals()['Project']('/REST/projects/%s'%ID, self._intf)

    def projects(self, id_filter='*'):
        """ Returns the list of all visible projects for the server.

            Parameters
            ----------
            id_filter: string
                Name pattern to filter the returned projects.
        """
        return globals()['Projects']('/REST/projects', self._intf, id_filter)

    def __repr__(self):
        return '<Root Object>'

    def __call__(self, datatype_or_path, columns=[]):
        """ Select clause to specify what type of data is to be returned.

            Parameters
            ----------
            datatype_or_path: string
                Can either be a resource path or a datatype:
                 - when a path, REST resources are returned, the `columns` 
                   argument is useless.
                 - when a datatype, a search Object is returned, the `columns`
                   argument has to be specified.
            columns: list
                List of fieldtypes e.g. xnat:subjectData/SUBJECT_ID
                Datatype and columns are used to specify the search table that
                has to be returned. Use the method `where` on the `Search` object
                to trigger a search on the database.
        """
        if datatype_or_path  in ['/', '//', '/REST']:
            return self

        if datatype_or_path.startswith('/REST'):
            datatype_or_path = datatype_or_path.split('/REST')[1]

        if datatype_or_path.startswith('/'):
            return_list = []

            try:
                for path in compute(datatype_or_path):
                    if DEBUG:
                        print 'path: %s'%path

                    pairs = zip(path.split('/')[1::2], path.split('/')[2::2])

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
                raise Exception('Invalid Syntax: %s'%datatype_or_path)            

        else:
            return Search(datatype_or_path, columns, self._intf)

