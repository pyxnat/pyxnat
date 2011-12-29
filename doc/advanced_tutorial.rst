==============================
Advanced Tutorial
==============================

.. currentmodule:: pyxnat

This advanced tutorial is not much more complicated than the starters
one. It just goes over parts of the API that may be less used (not
that they are less useful!) and that are more likely to change in
future releases.

Introspection
-------------

In order to browse a database people have to be aware of:
    - the REST hierarchy
    - schema types and fields
    - values of fields and resources within a project

The idea of this interface is to help users find their way around a
XNAT server by making it easier to gather the preceding information.

Searchable datatypes and fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> # simple datatypes listing
>>> central.inspect.datatypes()
[..., 'xnat:subjectData', 'xnat:projectData', 'xnat:mrSessionData',  ...]
>>> # datatypes listing with filter
>>> central.inspect.datatypes('cnda:*')
['cnda:manualVolumetryData',
 'cnda:clinicalAssessmentData',
 'cnda:psychometricsData',
 'cnda:dtiData',
 'cnda:atlasScalingFactorData',
 'cnda:segmentationFastData',
 'cnda:modifiedScheltensData']
>>> # simple fields listing
>>> central.inspect.datatypes('xnat:subjectData')
['xnat:subjectData/SUBJECT_ID',
 'xnat:subjectData/INSERT_DATE',
 'xnat:subjectData/INSERT_USER',
 'xnat:subjectData/GENDER_TEXT',
 ...]
>>> # field listing with filter
>>> central.inspect.datatypes('xnat:subjectData', '*ID*')
['xnat:subjectData/SUBJECT_ID', 'xnat:subjectData/ADD_IDS']
>>> # field listing on multiple types
>>> central.inspect.datatypes('cnda:*', 'EXPT_ID')
['cnda:manualVolumetryData/EXPT_ID',
 'cnda:clinicalAssessmentData/EXPT_ID',
 'cnda:psychometricsData/EXPT_ID',
 'cnda:dtiData/EXPT_ID',
 'cnda:atlasScalingFactorData/EXPT_ID',
 'cnda:segmentationFastData/EXPT_ID',
 'cnda:modifiedScheltensData/EXPT_ID']

To known what values fields can take in the database::

>>> central.inspect.field_values('xnat:mrSessionData/SESSION_ID')


REST hierarchy
~~~~~~~~~~~~~~

pyxnat does not support all the REST resources. The reasons for this
is that, some of these resources are still experimental, or do not
work exactly the same way which would make it difficult to provide a
consistent interface at the Python level. However support for these
exotic resources will increase in future releases. A good way to know
what is the supported REST hierarchy is to use the following method::

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

Naming conventions
~~~~~~~~~~~~~~~~~~

Administrators usually use a consistent vocabulary across single
projects, that maps to XNAT datatypes. A new feature in introduced in
0.6 and improved in 0.7 is to be able to define a mapping so that
specific name patterns can be used to cast a resource when creating a
new one.

For example with the following mapping::

    '/projects/my_project/subjects/*/experiments/SessionA_*':'xnat:mrSessionData'

Creating an experiment in ``my_project`` that matches `Session_*`, creates an `xnat:mrSessionData`::

    >>> central.select('/projects/my_project/subjects/*/experiments/SessionA_new').create()

In the 0.7, it is no longer up to the user to manually save and load
the mapping file. Files are created automatically and the mappings are
discovered `on the fly` when queries are issued on the server. Files
are loaded at the ``Interface`` creation and the mappings are updated
regularly. This functionality can be configured with the following
method::

    >>> # activate (default)
    >>> central.inspect.set_autolearn('True')
    >>> # setup update frequency
    >>> central.inspect.set_autolearn(tick=10)

When a mapping is available, re-running the ``rest_hierarchy`` method will display additional information such as::

    - PROJECTS
        + SUBJECTS
            + EXPERIMENTS
              -----------
            - xnat:mrSessionData
            - xnat:petSessionData
                +ASSESSORS
                ....


There are additional methods to visualize and display the mappings::

      >>> central.inspect.experiment_types()
      >>> central.inspect.assessor_types()
      >>> central.inspect.scan_types()
      >>> central.inspect.reconstruction_types()

Methods also allow to have a quick look on the values at those levels
on the database::

      >>> central.inspect.experiment_values('xnat:mrSessionData')
      >>> central.inspect.assessor_values('xnat:mrSessionData')
      >>> central.inspect.scan_values('xnat:mrSessionData')
      >>> central.inspect.reconstruction_values('xnat:mrSessionData')

For more details check the reference documentation.

.. note:: 
    With ``networkx`` and ``matplotlib`` installed, a ``draw``
    subinterface will be made available to display some data from the
    inspect subinterface as a graph::
    
    >>> central.draw.experiments()
    >>> central.draw.assessors()
    >>> central.draw.scans()
    >>> central.draw.reconstructions()
    >>> central.draw.architecture()
    >>> central.draw.field_values()


Sharing
-------

It is possible to share ``Subjects``, ``Experiments`` and
``Assessors`` via the REST API.  The methods to control sharing are::

    >>> subject = interface.select('/project/project1/subject/subject1')
    >>> subject.share('project2')
    >>> subject.unshare('project2')
    >>> # to know to in which projects a subject is available
    >>> subject.shares()

Almost the same interface is available for collection objects::

    >>> subjects = interface.select('/project/project1/subjects')
    >>> subjects.share('project2')
    >>> subjects.unshare('project2')
    >>> # to retrieve the subjects sharing a list of projects
    >>> subjects.sharing(['project1', 'project2'])

.. note::
    Of course the permissions policies (user level and project
    accessibility)still apply.

.. warning::
    The ``shares`` and ``sharing`` methods are not implemented in an
    efficient way at the moment. There is another more concerning
    issue: subjects for example are accessible through their ID or
    label. But labels stop working when trying to access a subject
    through a project that is not its orginial one.


Search templates
---------------

PyXNAT is also able to define templates to use with XNAT search engine.
They work basically the same way as usual searches but instead of defining
values to filter the data, one need to define keywords to replace them later
with the actual values::


    >>> contraints = [('xnat:subjectData/SUBJECT_ID','LIKE','subject_id'),
                      ('xnat:subjectData/PROJECT', '=', 'project_id'),
                      'OR',
                      [('xnat:subjectData/AGE','>','age'),
                       'AND'
                       ]
                      ]
    >>> columns = ['xnat:subjectData/PROJECT', 'xnat:subjectData/SUBJECT_ID']
    >>> interface.manage.search.save_template('name', 
                                               'xnat:subjectData',
					       columns,
					       criteria,
					       sharing='public',
					       description='my first template'
					       )
    >>>	interface.manage.search.use_template('name', 
                                             {'subject_id':'%',
					      'project_id':'my_project',
					      'age':'42'
					      }
					     )
    >>> interface.select(...).where(template=('name', 
                                              {'subject_id':'%',
					      'project_id':'my_project',
					      'age':'42'}
					      )
		                    )

And now it is also possible to re-use saved searches in the where clause in the
same way as the templates. It means that you re-use the contraints but not the
data selection which still changes:

     >>> interface.select(...).where(query='saved_name')

Provenance definition
--------------------

PyXNAT 0.8 introduces a way to store provenance i.e. to describe the steps 
that were performed on an initial data to produce this one. Reconstructions
and assessors only can be annotated with provenace information:

    >>> prov = {'program':'young',
                'timestamp':'2011-03-01T12:01:01.897987', 
                'user':'angus', 
                'machine':'war', 
                'platform':'linux',
                }
    >>> element.provenance.attach(prov)
    >>> element.provenance.get()
    >>> element.dettach()

The provenance attach method adds new steps with each call, unless the overwrite 
parameter is set to True. The following keywords for the provenance dictionnay are available:

    - program
    - program_version
    - program_arguments
    - timestamp
    - cvs
    - user
    - machine
    - platform
    - platform_version
    - compiler
    - compiler_version
