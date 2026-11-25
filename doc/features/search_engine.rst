The Search Engine
------------------

Querying the Database
~~~~~~~~~~~~~~~~~~~~~

XNAT search engine can be queried via the REST model. It can be
used to retrieve a specific subset of REST resources or a table
containing the relevant values. The following queries find all the
subjects that are within `my_project` or that have an age superior to
14.

Writing the query constraints:

.. code-block:: python

    >>> contraints = [('xnat:subjectData/SUBJECT_ID','LIKE','%'),
    ...               ('xnat:subjectData/PROJECT', '=', 'my_project'),
    ...                'OR',
    ...                [('xnat:subjectData/AGE','>','14'),
    ...                 'AND'
    ...                 ]
    ...                ]

Combining the ``select`` statement and the ``where`` clause to retrieve
the results. The result set will depend on the ``select`` which accepts
paths to resources, or a specification of a table datasets with variables
from the schema.

.. code-block:: python

    >>> central.select('//experiments').where(contraints)
    >>> central.select('xnat:subjectData', 
    ...		       ['xnat:subjectData/SUBJECT_ID', 
    ... 	        'xnat:subjectData/AGE']
    ...		).where(constraints)


.. note:: For additional documentation on the Search Engine:
   - :class:`~pyxnat.Search`
   - :class:`~pyxnat.SearchManager`
   - :class:`~pyxnat.CObject`

The query syntax
~~~~~~~~~~~~~~~~

Constraints for the ``where`` clause are expressed as follows:

	    - A query is an unordered list that contains
                    - 1 or more constraint(s)
                    - 0 or more sub-queries (lists as this one)
                    - 1 comparison method between the constraints
                        ('AND' or 'OR')
	    - A constraint is an ordered tuple that contains
                    - 1 valid searchable_type/searchable_field
                    - 1 operator among '=', '<', '>', '<=', '>=', 'LIKE'

Search Help
~~~~~~~~~~~

To get the searchable types and fields to put in the contraints, rows
and columns parameters, use the :func:`~pyxnat.Interface.inspect.datatypes``
method:

.. code-block:: python

    >>> central.inspect.datatypes(optional_filter)
    [..., 'xnat:subjectData', 'xnat:projectData', 'xnat:mrSessionData',  ...]
    >>> central.inspect.datatypes('xnat:subjectData', optional_filter)
    ['xnat:subjectData/SUBJECT_ID',
     'xnat:subjectData/INSERT_DATE',
     'xnat:subjectData/INSERT_USER',
     'xnat:subjectData/GENDER_TEXT',
     ...]

.. tip:: 
   How to get all the results in a query?

   .. code-block:: python

       >>> central.select('xnat:subjectData', 
       ... 		  ['xnat:subjectData/SUBJECT_ID', 
       ...		   'xnat:subjectData/AGE']).all()

   How to get all the columns from a datatype?

   .. code-block:: python

       >>> table = central.select('xnat:subjectData').where(...)

   Then to get everything:

   .. code-block:: python

      >>> table = central.select('xnat:subjectData').all()

Search Templates
~~~~~~~~~~~~~~~~

**pyxnat** offers a templating feature for the search engine. The first
thing is to create a template. The syntax is the same as for saving a
normal search, but values in the contraints must be keys to be re-used
in the future. In the following example ``sid`` is a key for the subject
identifiers.

.. code-block:: python
   
   >>> central.manage.search.save_template(
   ...		'template_name',
   ...		'xnat:subjectData',
   ...		['xnat:subjectData/PROJECT', 'xnat:subjectData/SUBHECT_ID'],
   ...		[('xnat:subjectData/SUBJECT_ID', 'LIKE', 'sid'), 'AND'])


To use the template, the easiest way is through the search manager.

.. code-block:: python
   
   >>> central.manage.search.use_template('template_name', 
   ...                                    {'sid':'*5*'})
   >>> central.manage.search.use_template('template_name', 
   ...                                    {'sid':'CENTRAL'})

It can also be used with the usual syntax with the ``select`` statement.
In that case only the constraints will be used because the return
data is re-defined in the select statement.

.. code-block:: python

   >>> central.select('//subjects').where(template=('my_template', 
   ... 					            {'sid':'*5*'}))
   >>> central.select('xnat:mrSessionData', 
   ... 	              ['xnat:mrSessionData/SESSION_ID']
   ... 		      ).where(template=('my_template', {'sid':'*5*'}))

.. warning:: This functionality hacks a bit the search saving system
   of XNAT. The only problem is that it will create saved searches
   that will be names ``template_something`` that will not work from
   the web interface. Do not use this feature if it is an issue for you.

.. note:: For additional documentation on templates:
   - :func:`~pyxnat.SearchManager.use_template`
   - :func:`~pyxnat.SearchManager.saved_template`
   - :func:`~pyxnat.SearchManager.save_template`
   - :func:`~pyxnat.SearchManager.get_template`
