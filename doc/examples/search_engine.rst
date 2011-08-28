
The search engine
------------------

The XNAT search engine can be queried via the REST model. It can be
used to retrieve a specific subset of REST resources or a table
containing the relevant values. The following queries find all the
subjects that are within `my_project` or that have an age superior to
14::

    >>> contraints = [('xnat:subjectData/SUBJECT_ID','LIKE','%'),
                      ('xnat:subjectData/PROJECT', '=', 'my_project'),
                      'OR',
                      [('xnat:subjectData/AGE','>','14'),
                       'AND'
                       ]
                      ]
    >>> # retrieve experiments
    >>> central.select('//experiments').where(contraints)
    >>> # retrieve table with one subject per row and the columns SUBJECT_ID and AGE
    >>> central.select('xnat:subjectData', ['xnat:subjectData/SUBJECT_ID', 'xnat:subjectData/AGE']).where(contraints)

See the ``Search``, ``SeachManager`` and ``CObject`` classes reference
documentation for further details.

To get the searchable types and fields to put in the contraints, rows
and columns parameters, use the ``Interface.inspect.datatypes``
method::

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
       >>> central.select('xnat:subjectData', 
       	   			['xnat:subjectData/SUBJECT_ID', 
       		                 'xnat:subjectData/AGE']).all()

.. tip:: 
   How to get all the columns from a datatype?
       >>> table = central.select('xnat:subjectData').where(...)

.. tip:: 
   Then to get everything:
   	>>> table = central.select('xnat:subjectData').all()
