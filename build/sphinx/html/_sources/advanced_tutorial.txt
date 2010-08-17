==============================
Advanced Tutorial
==============================

.. currentmodule:: pyxnat

This advanced tutorial is not much more complicated than the starters one. It just
goes over parts of the API that may be less used (not that they are less useful!) and
that are more likely to change in future releases.

Introspection
-------------

In order to browse a database people have to be aware of:
    - the REST hierarchy
    - schema types and fields
    - values of fields and resources within a project

The idea of this interface is to help users find their way around a XNAT server 
by making it easier to gather the preceding information.

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

>>> central.inspect.fieldvalues('xnat:mrSessionData/SESSION_ID')


REST hierarchy
~~~~~~~~~~~~~~

pyxnat does not support all the REST resources. The reasons for this is that, some
of these resources are still experimental, or do not work exactly the same way which
would make it difficult to provide a consistent interface at the Python level.
However support for these exotic resources will increase in future releases. A good
way to know what is the supported REST hierarchy is to use the following method:

>>> central.inspect.rest_hierarchy()
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

Administrators usually use a consistent vocabulary across single projects, 
that maps to XNAT datatypes. A new feature in 0.6 is to be able to define a mapping 
so that specific name patterns can be used to cast a resource when creating a new one.

For example with the following mapping::

    '/projects/my_project/subjects/*/experiments/SessionA_*':'xnat:mrSessionData'

Creating an experiment in ``my_project`` that matches `Session_*`, creates an `xnat:mrSessionData`::

    >>> central.select('/projects/my_project/subjects/*/experiments/SessionA_new').create()

There are two ways to have the mapping. 
First, edit, save and load manually a file::

    >>> central.inspect.update(location)
    >>> central.inspect.save(location)
    >>> central.inspect.clear()

Second, find automatically a mapping for a specific project with a function that goes through the REST resources::

    >>> central.inspect('my_project', subjects_nb=2)

When using this method, the user still has to save the information to a file and load it back.
To retrieve the mapping as a dictionnary::

    >>> central.inspect.naming_conventions()

When a mapping is available, re-running the ``rest_hierarchy`` method will display additional information such as::

    - PROJECTS
        + SUBJECTS
            + EXPERIMENTS
              -----------
            - xnat:mrSessionData
            - xnat:petSessionData
                +ASSESSORS
                ....

.. note::
    With ``networkx`` and ``matplotlib`` installed, it is possible to have a graph
    representation of the naming conventions and xnat types mapping.
    
    >>> central.inspect.naming_conventions(as_graph=True)
    >>> central.inspect.rest_hierarchy(as_graph=True)

.. warning::
    
    The API regarding the naming conventions is not definitive. I am quite positive
    I will change it in a future release. The code needs refactoring here as well.


Sharing
-------

It is possible to share ``Subjects``, ``Experiments`` and ``Assessors`` via the REST API.
The methods to control sharing are::

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

    Of course the permissions policies (user level and project accessibility) still apply.

.. warning::

    The ``shares`` and ``sharing`` methods are not implemented in an efficient way at the
    moment. There is another more concerning issue: subjects for example are accessible
    through their ID or label. But labels stop working when trying to access a subject
    through a project that is not its orginial one.


    
