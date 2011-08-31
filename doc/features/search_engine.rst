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
    ...		).where(contraints)


.. note:: For additional documentation on the Search Engine:
   - :class:`~pyxnat.Search`
   - :class:`~pyxnat.SearchManager`
   - :class:`~pyxnat.CObject`

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
