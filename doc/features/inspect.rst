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
