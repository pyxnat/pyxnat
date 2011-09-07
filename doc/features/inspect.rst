XNAT Introspection
------------------

Prior knowledge is needed to traverse an XNAT database, general knowledge
on XNAT, such as the REST hierarchy, a knowledge specific to a database
such as datatypes and values of variables.  The idea of this features 
is to help users find their way around an XNAT server by making it easier
to gather intformation.

The REST hierarchy
~~~~~~~~~~~~~~~~~~

The REST hierarchy is the first thing to know. It can be found on the
`XNAT web site <http://docs.xnat.org/XNAT+REST+API>`_ or printed on screen:

.. code-block:: python

   >>> central.inspect.structure()
       - PROJECTS
       	 + SUBJECTS
	   + EXPERIMENTS
	     + ASSESSORS
	       + RESOURCES
	       	 + FILES
               + IN_RESOURCES
	       	 + FILES
               + OUT_RESOURCES
	       	 + FILES
	     + RECONSTRUCTIONS
               + IN_RESOURCES
                 + FILES
               + OUT_RESOURCES
                 + FILES
             + SCANS
               + RESOURCES
               	 + FILES
             + RESOURCES
	       + FILES
           + RESOURCES
             + FILES
         + RESOURCES
           + FILES

Searchable datatypes and fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To write queries for the search engine, or just to have a better insight
of the data within an XNAT instance users have to know about datatypes
and data values. There are a few methods in the 
:class:`~pyxnat.Interface.inspect` sub-interface to get this information.

Get the datatypes:

.. code-block:: python

   >>> central.inspect.datatypes()
   [..., 'xnat:subjectData', 'xnat:projectData', 'xnat:mrSessionData',  ...]
   >>> central.inspect.datatypes('cnda:*')
   ['cnda:manualVolumetryData',
    'cnda:clinicalAssessmentData',
    'cnda:psychometricsData',
    'cnda:dtiData',
    'cnda:atlasScalingFactorData',
    'cnda:segmentationFastData',
    'cnda:modifiedScheltensData']

Get the fields:

.. code-block:: python

   >>> central.inspect.datatypes('xnat:subjectData')
   ['xnat:subjectData/SUBJECT_ID',
    'xnat:subjectData/INSERT_DATE',
    'xnat:subjectData/INSERT_USER',
    'xnat:subjectData/GENDER_TEXT']
   >>> central.inspect.datatypes('xnat:subjectData', '*ID*')
   ['xnat:subjectData/SUBJECT_ID', 'xnat:subjectData/ADD_IDS']
   >>> central.inspect.datatypes('cnda:*', 'EXPT_ID')
   ['cnda:manualVolumetryData/EXPT_ID',
    'cnda:clinicalAssessmentData/EXPT_ID',
    'cnda:psychometricsData/EXPT_ID',
    'cnda:dtiData/EXPT_ID',
    'cnda:atlasScalingFactorData/EXPT_ID',
    'cnda:segmentationFastData/EXPT_ID',
    'cnda:modifiedScheltensData/EXPT_ID']

Get the field values in an XNAT instance:

.. code-block:: python

   >>> central.inspect.field_values('xnat:mrSessionData/SESSION_ID')


Resources organization
~~~~~~~~~~~~~~~~~~~~~~

It is also useful to have a preview, even  incomplete, of the resources 
names and values in the REST tree. The REST resources map to datatypes
defined in the schema. It's not possible to guess the mapping but 
**pyxnat** provides methods to retrieve it:

.. code-block:: python

      >>> central.inspect.experiment_types()
      >>> central.inspect.assessor_types()
      >>> central.inspect.scan_types()
      >>> central.inspect.reconstruction_types()

Methods also enable to have a quick look on the values at those levels
on the database:

.. code-block:: python

      >>> central.inspect.experiment_values('xnat:mrSessionData')
      >>> central.inspect.assessor_values('xnat:mrSessionData')
      >>> central.inspect.scan_values('xnat:mrSessionData')
      >>> central.inspect.reconstruction_values('xnat:mrSessionData')

The mappings can also be used to create a resource by guessing its type.
For example all the resources at the experiment level named ``Session_*``
are ``xnat:mrSessionData`` so the following line will create an 
``xnat:mrSessionData``:

.. code-block:: python

    >>> exp = subject.experiment('SessionA_new').insert()
    >>> exp.datatype()
    'xnat:mrSessionData'

When a mapping is available, re-running the 
:func:`~pyxnat.Interface.inspect.structure` method will display additional 
information such as:

.. code-block:: python

   >>> central.inspect.structure()
   ... - PROJECTS
   ...  + SUBJECTS
   ...    + EXPERIMENTS
   ...    -----------
   ...    - xnat:mrSessionData
   ...    - xnat:petSessionData
   ...	    +ASSESSORS
   ...	    ...

.. note:: A bit more on how the mapping are discovered:
   Administrators usually use a consistent vocabulary across single
   projects, that maps to XNAT datatypes. A new feature introduced in
   0.6 and improved in 0.7 is to be able to define a mapping so that
   specific name patterns can be used to cast a resource when creating a
   new one. In the 0.7, it is no longer up to the user to manually save 
   and load the mapping file. Files are created automatically and the 
   mappings are discovered on the fly when queries are issued on the 
   server. Files are loaded at the :class:`~pyxnat:Interface` creation 
   and the mappings are updated regularly. A small example:

   .. code-block:: python

      {'/projects/my_project/subjects/*/experiments/SessionA_*':'xnat:mrSessionData'}

