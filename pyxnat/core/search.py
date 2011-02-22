import csv
import difflib
from StringIO import StringIO

from lxml import etree
from .jsonutil import JsonTable, get_column, get_where
from .errors import is_xnat_error, catch_error
from .errors import ProgrammingError, NotSupportedError
from .errors import DataError, DatabaseError

search_nsmap = {'xdat':'http://nrg.wustl.edu/security',
                'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

special_ops = {'*':'%',}


def build_search_document(root_element_name, columns, criteria_set, 
                               brief_description='', allowed_users=[]):
    root_node = \
        etree.Element(etree.QName(search_nsmap['xdat'], 'bundle'),
                      nsmap=search_nsmap
                      )

    root_node.set('ID', "@%s" % root_element_name)
    root_node.set('brief-description', brief_description)
    root_node.set('allow-diff-columns', "0")
    root_node.set('secure', "false")

    root_element_name_node = \
        etree.Element(etree.QName(search_nsmap['xdat'], 'root_element_name'),
                      nsmap=search_nsmap
                      )

    root_element_name_node.text = root_element_name

    root_node.append(root_element_name_node)

    for i, column in enumerate(columns):
        element_name, field_ID = column.split('/')

        search_field_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'search_field'), 
                          nsmap=search_nsmap
                          )

        element_name_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'element_name'), 
                          nsmap=search_nsmap
                          )

        element_name_node.text = element_name

        field_ID_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'field_ID'), 
                          nsmap=search_nsmap
                          )

        field_ID_node.text = field_ID

        sequence_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'sequence'), 
                          nsmap=search_nsmap
                          )

        sequence_node.text = str(i)

        type_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'type'), 
                          nsmap=search_nsmap
                          )

        type_node.text = 'string'

        header_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'header'), 
                          nsmap=search_nsmap
                          )

        header_node.text = column

        search_field_node.extend([element_name_node,
                                  field_ID_node,
                                  sequence_node,
                                  type_node, header_node
                                  ])

        root_node.append(search_field_node)

    search_where_node = \
        etree.Element(etree.QName(search_nsmap['xdat'], 'search_where'), 
                      nsmap=search_nsmap
                      )

    root_node.append(build_criteria_set(search_where_node, criteria_set))

    if allowed_users != []:

        allowed_users_node = \
            etree.Element(etree.QName(search_nsmap['xdat'], 'allowed_user'), 
                          nsmap=search_nsmap
                          )

        for allowed_user in allowed_users:
            login_node = \
                etree.Element(etree.QName(search_nsmap['xdat'], 'login'), 
                              nsmap=search_nsmap
                              )
            login_node.text = allowed_user
            allowed_users_node.append(login_node)

        root_node.append(allowed_users_node)

    return etree.tostring(root_node.getroottree())

def build_criteria_set(container_node, criteria_set):

    for criteria in criteria_set:
        if isinstance(criteria, basestring):
            container_node.set('method', criteria)

        if isinstance(criteria, (list)):
            sub_container_node = \
                etree.Element(etree.QName(search_nsmap['xdat'], 'child_set'),
                              nsmap=search_nsmap
                              )

            container_node.append(
                build_criteria_set(sub_container_node, criteria))

        if isinstance(criteria, (tuple)):
            if len(criteria) != 3:
                raise ProgrammingError('%s should be a 3-element tuple' % 
                                        str(criteria)
                                        )

            constraint_node = \
                etree.Element(etree.QName(search_nsmap['xdat'], 'criteria'), 
                              nsmap=search_nsmap
                              )

            constraint_node.set('override_value_formatting', '0')

            schema_field_node = \
                etree.Element(etree.QName(search_nsmap['xdat'],
                                          'schema_field'
                                          ), 
                              nsmap=search_nsmap
                              )

            schema_field_node.text = criteria[0]

            comparison_type_node = \
                etree.Element(etree.QName(search_nsmap['xdat'],
                                          'comparison_type'
                                          ), 
                              nsmap=search_nsmap
                              )

            comparison_type_node.text = special_ops.get(criteria[1], 
                                                        criteria[1]
                                                        )

            value_node = \
                etree.Element(etree.QName(search_nsmap['xdat'], 'value'),
                              nsmap=search_nsmap
                              )

            value_node.text = criteria[2].replace('*', special_ops['*'])

            constraint_node.extend([
                    schema_field_node, comparison_type_node, value_node])

            container_node.append(constraint_node)

    return container_node

def rpn_contraints(rpn_exp):
    left = []
    right = []
    triple = []

    for i, t in enumerate(rpn_exp.split()):
        if t in ['AND', 'OR']:
            if 'AND' in right or 'OR' in right and left == []:
                try:
                    operator = right.pop(right.index('AND'))
                except:
                    operator = right.pop(right.index('OR'))

                left = [right[0]]
                left.append(right[1:] + [t])
                left.append(operator)

                right = []

            elif right != []:
                right.append(t)

                if left != []:
                    left.append(right)
                else:
                    left = right[:]
                    right = []

            elif right == [] and left != []:
                left = [left]
                left.append(t)
                right = left[:]
                left = []
            else:
                raise ProgrammingError('in expression %s' % rpn_exp)

        else:
            triple.append(t)
            if len(triple) == 3:
                right.append(tuple(triple))
                triple = []

    return left if left != [] else right

# ---------------------------------------------------------------

class SearchManager(object):
    """ Search interface. 
        Handles operations to save and get back searches on the server.

        Examples
        --------
            >>> row = 'xnat:subjectData'
            >>> columns = ['xnat:subjectData/PROJECT',
                           'xnat:subjectData/SUBJECT_ID'
                           ]
            >>> criteria = [('xnat:subjectData/SUBJECT_ID', 'LIKE', '*'), 
                            'AND'
                            ]
            >>> interface.manage.search.save('mysearch', row, columns,
                                             criteria, sharing='public'
                                             )
    """
    def __init__(self, interface):
        self._intf = interface

    def save(self, name, row, columns, constraints, sharing='private'):
        """ Saves a query on the XNAT server.

            Parameters
            ----------
            name: string
                Name of the query displayed on the Web Interface and
                used to get back the results.
            row: string
                Datatype from `Interface.inspect.datatypes()`.
                Usually ``xnat:subjectData``
            columns: list
                List of data fields from 
                `Interface.inspect.datatypes('*', '*')`
            constraints: list
                See also: `Search.where()`
            sharing: string | list
                Define by whom the query is visible.
                If sharing is a string it may be either 
                ``private`` or ``public``.
                Otherwise a list of valid logins for the XNAT server 
                from `Interface.users()`.

            See Also
            --------
            Search.where
        """
        name = name.replace(' ', '_')
        if sharing == 'private':
            users = [self._intf._user]
        elif sharing == 'public':
            users = []
        elif isinstance(sharing, list):
            users = sharing
        else:
            raise NotSupportedError('Share mode %s not valid' % sharing)

        self._intf._exec('/REST/search/saved/%s?inbody=true' % name, 
                         method='PUT', 
                         body=build_search_document(row, columns, 
                                                    constraints, 
                                                    name, users
                                                    )
                         )

    def saved(self):
        """ Returns the names of accessible saved search on the server.
        """

        jdata = self._intf._get_json('/REST/search/saved?format=json')
        return get_column(jdata, 'brief_description')
    
    def get(self, name):
        """ Returns the results of the query saved on the XNAT server.
        """

        jdata = self._intf._get_json('/REST/search/saved?format=json')
        
        try:
            search_id = get_where(jdata, brief_description=name)[0]['id']
        except IndexError:
            raise DatabaseError('%s not found' % name)

        content = self._intf._exec(
            '/REST/search/saved/%s/results?format=csv' % search_id, 'GET')

        results = csv.reader(StringIO(content), delimiter=',', quotechar='"')
        headers = results.next()

        return JsonTable([dict(zip(headers, res)) 
                          for res in results
                          ],
                         headers
                         )

    def delete(self, name):
        """ Removes the search from the server.
        """
        jdata = self._intf._get_json('/REST/search/saved?format=json')
        
        try:
            search_id = get_where(jdata, brief_description=name)[0]['id']
        except IndexError:
            raise DatabaseError('%s not found' % name)

        self._intf._exec('/REST/search/saved/%s'%search_id, 'DELETE')

    def eval_rpn_exp(self, rpnexp):
        return rpn_contraints(rpnexp)


class Search(object):
    """ Define constraints to make a complex search on the database.

        This :class:`Search` is available at different places throughout
        the API:

            >>> interface.select(DATA_SELECTION).where(QUERY)
            >>> interface.manage.search.save('name', TABLE_DEFINITION, QUERY)

        Examples
        --------
            >>> query = [('xnat:subjectData/SUBJECT_ID', 'LIKE', '%'), 
                         ('xnat:projectData/ID', '=', 'my_project'),
                         [('xnat:subjectData/AGE', '>', '14'),
                           'AND'
                          ],
                         'OR'
                        ]
    """
    def __init__(self, row, columns, interface):
        """ Configure the result table.

            Parameters
            ----------
            row: string
                The returned table will have one line for every matching
                occurence of this type.
                e.g. xnat:subjectData 
                --> table with one line per matching subject
            columns: list
                The returned table will have all the given columns.
        """
        self._row = row
        self._columns = columns
        self._intf = interface

    def where(self, constraints):
        """ Triggers the search.

            Parameters
            ----------
            contraints: list
                A query is an unordered list that contains
                    - 1 or more constraints
                    - 0 or more sub-queries (lists as this one)
                    - 1 comparison method between the constraints 
                        ('AND' or 'OR')
                A constraint is an ordered tuple that contains
                    - 1 valid searchable_type/searchable_field
                    - 1 operator among '=', '<', '>', '<=', '>=', 'LIKE'

            Returns
            -------
            results: JsonTable object
                An table-like object containing the results. It is 
                basically a list of dictionaries that has additional 
                helper methods.
        """
        if isinstance(constraints, basestring):
            constraints = rpn_contraints(constraints)

        bundle = build_search_document(self._row, self._columns, constraints)

        content = self._intf._exec("/REST/search?format=csv", 'POST', bundle)

        if is_xnat_error(content):
            catch_error(content)

        results = csv.reader(StringIO(content), delimiter=',', quotechar='"')
        headers = results.next()

        headers_of_interest = []

        for column in self._columns:
            headers_of_interest.append(
                difflib.get_close_matches(
                    column.split(self._row+'/')[0].lower() \
                        or column.split(self._row+'/')[1].lower(), 
                    headers)[0]
                )

        if len(self._columns) != len(headers_of_interest):
            raise DataError('unvalid response headers')

        return JsonTable([dict(zip(headers, res)) for res in results], 
                         headers_of_interest).select(headers_of_interest)

    def all(self):
        return self.where([(self._row+'/ID', 'LIKE', '%'), 'AND'])

