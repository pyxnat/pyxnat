import os
import re
import glob
import csv
import difflib
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from lxml import etree
import json

from .jsonutil import JsonTable, get_column, get_where, get_selection
from .errors import is_xnat_error, catch_error
from .errors import ProgrammingError, NotSupportedError
from .errors import DataError, DatabaseError
from .uriutil import check_entry

search_nsmap = {'xdat':'http://nrg.wustl.edu/security',
                'xsi':'http://www.w3.org/2001/XMLSchema-instance'}

special_ops = {'*':'%', }


def build_search_document(root_element_name, columns, criteria_set,
                          brief_description='', long_description='',
                          allowed_users=[]):
    root_node = \
        etree.Element(etree.QName(search_nsmap['xdat'], 'bundle'),
                      nsmap=search_nsmap
                      )

    root_node.set('ID', "@%s" % root_element_name)
    root_node.set('brief-description', brief_description)
    root_node.set('description', long_description)
    root_node.set('allow-diff-columns', "0")
    root_node.set('secure', "false")

    root_element_name_node = \
        etree.Element(etree.QName(search_nsmap['xdat'], 'root_element_name'),
                      nsmap=search_nsmap
                      )

    root_element_name_node.text = root_element_name

    root_node.append(root_element_name_node)

    for i, column in enumerate(columns):
        element_name, field_ID = column.split('/', 1)

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

def query_from_xml(document):
    query = {}
    root = etree.fromstring(document)
    _nsmap = root.nsmap

    query['description'] = root.get('description', default="")

    query['row'] = root.xpath('xdat:root_element_name',
                              namespaces=root.nsmap)[0].text

    query['columns'] = []

    for node in root.xpath('xdat:search_field',
                           namespaces=_nsmap):

        en = node.xpath('xdat:element_name', namespaces=root.nsmap)[0].text
        fid = node.xpath('xdat:field_ID', namespaces=root.nsmap)[0].text

        query['columns'].append('%s/%s' % (en, fid))

    query['users'] = [
        node.text
        for node in root.xpath('xdat:allowed_user/xdat:login',
                               namespaces=root.nsmap
                               )
        ]

    try:
        search_where = root.xpath('xdat:search_where',
                                  namespaces=root.nsmap)[0]

        query['constraints'] = query_from_criteria_set(search_where)
    except:
        query['constraints'] = [('%s/ID' % query['row'], 'LIKE', '%'), 'AND']

    return query

def query_from_criteria_set(criteria_set):
    query = []
    query.append(criteria_set.get('method'))
    _nsmap = criteria_set.nsmap

    for criteria in criteria_set.xpath('xdat:criteria',
                                       namespaces=_nsmap):

        _f = criteria.xpath('xdat:schema_field', namespaces=_nsmap)[0]
        _o = criteria.xpath('xdat:comparison_type', namespaces=_nsmap)[0]
        _v = criteria.xpath('xdat:value', namespaces=_nsmap)[0]

        constraint = (_f.text, _o.text, _v.text)
        query.insert(0, constraint)

    for child_set in criteria_set.xpath('xdat:child_set',
                                        namespaces=_nsmap):

        query.insert(0, query_from_criteria_set(child_set))

    return query

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
                                             criteria, sharing='public',
                                             description='my first search'
                                             )
    """
    def __init__(self, interface):
        self._intf = interface

    def _save_search(self, row, columns, constraints, name, desc, sharing):
        self._intf._get_entry_point()

        name = name.replace(' ', '_')
        if sharing == 'private':
            users = [self._intf._user]
        elif sharing == 'public':
            users = []
        elif isinstance(sharing, list):
            users = sharing
        else:
            raise NotSupportedError('Share mode %s not valid' % sharing)

        self._intf._exec(
            '%s/search/saved/%s?inbody=true' % (self._intf._entry, name),
            method='PUT',
            body=build_search_document(row, columns,
                                       constraints,
                                       name, desc.replace('%', '%%'),
                                       users
                                       )
            )

    def save(self, name, row, columns, constraints,
             sharing='private', description=''):
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
        self._save_search(row, columns, constraints,
                          name, description, sharing)


    def saved(self, with_description=False):
        """ Returns the names of accessible saved search on the server.
        """
        self._intf._get_entry_point()

        jdata = self._intf._get_json(
            '%s/search/saved?format=json' % self._intf._entry)

        if with_description:
            return [(ld['brief_description'],
                     ld['description'].replace('%%', '%'))
                    for ld in get_selection(jdata, ['brief_description',
                                                    'description'
                                                    ]
                                            )
                    if not ld['brief_description'].startswith('template_')]
        else:
            return [name
                    for name in get_column(jdata, 'brief_description')
                    if not name.startswith('template_')]

    def get(self, name, out_format='results'):
        """ Returns the results of the query saved on the XNAT server or
            the query itself to know what it does.

            Parameters
            ----------
            name: string
                Name of the saved search. An exception is raised if the name
                does not exist.
            out_format: string
                Can take the following values:
                    - results to download the results of the search
                    - xml to download the XML document defining the search
                    - query to get the pyxnat representation of the search
        """
        self._intf._get_entry_point()

        jdata = self._intf._get_json(
            '%s/search/saved?format=json' % self._intf._entry)

        try:
            search_id = get_where(jdata, brief_description=name)[0]['id']
        except IndexError:
            raise DatabaseError('%s not found' % name)

        if out_format in ['xml', 'query']:
            bundle = self._intf._exec(
                '%s/search/saved/%s' % (self._intf._entry,
                                        search_id
                                        ), 'GET')

            if out_format == 'xml':
                return bundle
            else:
                return query_from_xml(bundle)


        content = self._intf._exec(
            '%s/search/saved/%s/results?format=csv' % (self._intf._entry,
                                                       search_id), 'GET')

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
        self._intf._get_entry_point()

        jdata = self._intf._get_json(
            '%s/search/saved?format=json' % self._intf._entry)

        try:
            search_id = get_where(jdata, brief_description=name)[0]['id']
        except IndexError:
            raise DatabaseError('%s not found' % name)

        self._intf._exec('%s/search/saved/%s' % (self._intf._entry,
                                                 search_id
                                                 ), 'DELETE')

    def save_template(self, name, row=None, columns=[],
                      constraints=[], sharing='private', description=''):
        """
            Define and save a search template. Same as the save method, but
            the values in the constraints are used as keywords for value
            replacement when using the template.

            Parameters
            ----------
            name: string
                Name under which the template is save in XNAT. A 'template_' is
                prepended to the name so that it appear clearly as a template
                on the web interface.
            row: string
                Datatype from `Interface.inspect.datatypes()`.
                Usually ``xnat:subjectData``
            columns: list
                List of data fields from
                `Interface.inspect.datatypes('*', '*')`
            constraints: list
                See also: `Search.where()`, values are keywords for the template
            sharing: string | list
                Define by whom the query is visible.
                If sharing is a string it may be either
                ``private`` or ``public``.
                Otherwise a list of valid logins for the XNAT server
                from `Interface.users()`.
        """


        def _make_template(query):
            query_template = []

            for constraint in query:
                if isinstance(constraint, tuple):
                    query_template.append((constraint[0],
                                           constraint[1],
                                           '%%(%s)s' % constraint[2])
                                          )
                elif isinstance(constraint, (unicode, str)):
                    query_template.append(constraint)
                elif isinstance(constraint, list):
                    query_template.append(_make_template(constraint))
                else:
                    raise ProgrammingError('Unrecognized token '
                                           'in query: %s' % constraint
                                           )

            return query_template

        self._save_search(
            row, columns, _make_template(constraints),
            'template_%s' % name, description, sharing
            )

    def saved_templates(self, with_description=False):
        """ Returns the names of accessible saved search templates on the server.
        """
        self._intf._get_entry_point()

        jdata = self._intf._get_json(
            '%s/search/saved?format=json' % self._intf._entry)

        if with_description:
            return [
                (ld['brief_description'].split('template_')[1],
                 ld['description'].replace('%%', '%')
                 )
                for ld in get_selection(jdata, ['brief_description',
                                                'description'
                                                ]
                                        )
                if ld['brief_description'].startswith('template_')
                ]
        else:
            return [name.split('template_')[1]
                    for name in get_column(jdata, 'brief_description')
                    if name.startswith('template_')]

    def use_template(self, name, values):
        """
            Parameters
            ----------
            name: string
                Name of the template.
            values: dict
                Values to put in the template, get the valid keys using
                the get_template method.

            Examples
            --------
            >>> interface.manage.search.use_template(name,
                          {'subject_id':'ID',
                           'age':'32'
                           })

        """
        self._intf._get_entry_point()

        bundle = self.get_template(name, True) % values

        # have to remove search_id information before re-posting it
        _query = query_from_xml(bundle)
        bundle = build_search_document(_query['row'],
                                       _query['columns'],
                                       _query['constraints']
                                       )

        content = self._intf._exec(
            "%s/search?format=csv" % self._intf._entry, 'POST', bundle)

        results = csv.reader(StringIO(content), delimiter=',', quotechar='"')
        headers = results.next()

        return JsonTable([dict(zip(headers, res))
                          for res in results
                          ],
                         headers
                         )

    def get_template(self, name, as_xml=False):
        """ Get a saved template, either as an xml document, or as a pyxnat
            representation, with the keys to be used in the template
            between the parentheses in %()s.

            Parameters
            ----------
            name: str
                Name under which the template is saved
            as_xml: boolean
                If True returns an XML document, else return a list of
                constraints. Defaults to False.
        """
        self._intf._get_entry_point()

        jdata = self._intf._get_json(
            '%s/search/saved?format=json' % self._intf._entry)

        try:
            search_id = get_where(jdata,
                                  brief_description='template_%s' % name
                                  )[0]['id']
        except IndexError:
            raise DatabaseError('%s not found' % name)

        bundle = self._intf._exec(
            '%s/search/saved/%s' % (self._intf._entry,
                                    search_id
                                    ), 'GET')

        if as_xml:
            return bundle
        else:
            _query = query_from_xml(bundle)
            return _query['row'], _query['columns'], _query['constraints'], _query['description']

    def delete_template(self, name):
        """ Deletes a search template.
        """
        self.delete('template_%s' % name)

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

    def where(self, constraints=None, template=None, query=None):
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
        self._intf._get_entry_point()

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
            raise ProgrammingError('One of contraints, template and query'
                                   'parameters must be correctly set.')

        bundle = build_search_document(self._row, self._columns, constraints)

        content = self._intf._exec(
            "%s/search?format=csv" % self._intf._entry, 'POST', bundle)

        if is_xnat_error(content):
            catch_error(content)

        results = csv.reader(StringIO(content), delimiter=',', quotechar='"')
        headers = results.next()

        headers_of_interest = []

        for column in self._columns:
            try:
                headers_of_interest.append(
                    difflib.get_close_matches(
                        column.split(self._row + '/')[0].lower() \
                            or column.split(self._row + '/')[1].lower(),
                        headers)[0]
                    )
            except IndexError:
                headers_of_interest.append('unknown')

        if len(self._columns) != len(headers_of_interest):
            raise DataError('unvalid response headers')

        return JsonTable([dict(zip(headers, res)) for res in results],
                         headers_of_interest).select(headers_of_interest)

    def all(self):
        return self.where([(self._row + '/ID', 'LIKE', '%'), 'AND'])

