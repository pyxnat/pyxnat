A few shorcuts
--------------

There are two competing interfaces in XNAT REST API to retrive array of 
values. One is the search engine, the other one is URIs with advanced
filtering. The search engine offers more flexibiblity but can be slower
in some cases. This is why **pyxnat** wraps some REST calls to list
all the experiments and scans from the server with the filering capabilities.


List all the experiments from an XNAT instance:

.. code-block:: python

   >>> central.array.experiments()

List all the experiments from an XNAT instance with some filters:

.. code-block:: python

   >>> central.array.experiments(project_id='my_project',
   ...				 subject_id='my_subject',
   ...				 experiment_id='my_expt',
   ...				 experiment_type='xnat:mrSessionData')

List all the experiments from an XNAT instance with custom filters. The
following call returns all the mrSessionData experiments whose subject
is 42 years old:

.. code-block:: python

   >>> central.array.experiments(constraints={'xnat:mrSessionData/age':'42'})

To customize the returned columns:

.. code-block:: python

   >>> central.array.experiments(columns=['xnat:mrSessionData/age'])

The syntax to list all scans is exactly the same:

.. code-block:: python

   >>> central.array.scans(project_id='my_project')

There is also a shortcut that uses the search engine to list all the 
experiments it combines the syntax from the previous shortcuts and the
syntax from the search engine to express the contraints.

.. code-block:: python

   >>> central.array.search_experiments(
   ...		project_id='my_project',
   ...		constraints=[('xnat:subjectData/AGE','>','14'), 'AND']
   ...		)

