==============================
Starters Tutorial
==============================

.. currentmodule:: pyxnat

This is a short tutorial going through the main features of this API.
Depending on the policy of the XNAT server you are using, and your
user level, you can have read and write access to a specific set of
resources. During this tutorial, we will use a `fake` standard user
account on the XNAT central repository, where you will have limited
access to a number of projects and full access to the projects you
own.

.. note:: 
    XNAT Central is a public XNAT repository managed by the XNAT team
    and updated regularly with the latest improvements of the
    development branch.
    
_____

.. [#]  http://central.xnat.org

Getting started
---------------

Connecting to a XNAT server requires valid credentials so you might want to
start by requesting those on the Web interface of your server. 

>>> from pyxnat import Interface
>>> central = Interface(
    	       server='http://central.xnat.org:8080',
               user='my_login',
               password='my_pass',
               cachedir=os.path.join(os.path.expanduser('~'), '.store')
               )

The cachedir argument specifies where the local disk-cache will be
stored.  Every query and downloaded file will be stored here so choose
a location with sufficient free space. If the datastore argument if
not given, a temporary location is picked automatically but it may be
flushed at every reboot of the machine. Here the cachedir argument is
set to a `.store` directory in the user's home directory in a cross
platform manner. If the `cachedir` starts getting full, a warning will
be printed in the stdout.

It is also possible to define an :class:`Interface` object without
specifying all the connection parameters. Pyxnat switches to
interactive mode and prompts the user for the missing information. In
that case the object checks that the parameters are correct by
connecting to the server.

>>> central = Interface(server='http://central.xnat.org:8080')
>>> User:my_login
>>> Password: 

You can also use a configuration file. The best way to create the file
is to use the ``save_config()`` method on an existing interface.

>>> central.save_config('central.cfg')
>>> central2 = Interface(config='central.cfg')

.. warning::
    Depending on the server configuration, you may have to include the port 
    in the server url, as well as the name of the XNAT tomcat application. 
    So you might end up with something like:
    http://server_ip:port/xnat

The main interface class is now divided into logical subinterfaces:
    - data selection
    - general management
    - cache management
    - server instrospection


Data selection
--------------

Now that we have an `Interface` object, we can start browsing the
server with the ``select`` subinterface which can be used, either with
expicit Python objects and methods, or through a ``path`` describing
the data.

Simple requests::

    >>> interface.select.projects().get()
    [..., u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]
    >>> interface.select('/projects').get()
    [..., u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]

Nested requests::

    >>> interface.select.projects().subjects().get()
    >>> interface.select('/projects/*/subjects').get()
    >>> interface.select('/projects/subjects').get()
    >>> interface.select('//subjects').get()
    ['IMAGEN_000000001274', 'IMAGEN_000000075717', ...,'IMAGEN_000099954902']

Filtered requests::

    >>> interface.select.projects('*OASIS_CS*').get()
    >>> interface.select('/projects/*OASIS_CS*').get()
    [u'CENTRAL_OASIS_CS']
    
    >>> interface.select.project('IMAGEN').subjects('*55*42*').get()
    >>> interface.select('/projects/IMAGEN/subjects/*55*42*').get()
    ['IMAGEN_000055203542', 'IMAGEN_000055982442', 'IMAGEN_000097555742']

Resources paths
---------------

The resources paths that can be passed as an argument to ``select`` is
a powerful tool but can easily generate thousands of queries so one
has to be careful when using it.

Absolute paths
~~~~~~~~~~~~~~

A full path to a resource is a sequence of resource level and
resource_id pairs::

	    /project/IMAGEN/subject/IMAGEN_000055982442

A full path to a resource listing is a sequence of resource level and
resource_id pairs finishing by a plural resource level (i.e. with an
's')::

	/project/IMAGEN/subject/IMAGEN_000055982442/experiments

The first nice thing here is that you actually don't have to worry about
resource level to be plural or singular within the path::

	 /project/IMAGEN/subject/IMAGEN_000055982442
	 EQUALS
	 /projects/IMAGEN/subjects/IMAGEN_000055982442

	 /project/IMAGEN/subject/IMAGEN_000055982442/experiments
	 EQUALS
	 /project/IMAGEN/subjects/IMAGEN_000055982442/experiment


Relative paths and shortcuts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When browsing resources, some levels are often left without any IDs
and filled with ``*`` filters instead, which leads to paths like::

    /projects/*/subjects/*/experiments/*

That can instead be written::

     /projects/subjects/experiments OR //experiments

To have all the experiments from a specific project::

   /project/IMAGEN//experiments 
   EQUALS
   /project/IMAGEN/subjects/*/experiments

The double slash syntax can be used anywhere in the path and any
number of time::

       //subjects//assessors 
       EQUALS 
       /projects/*/subjects/*/experiments/*/assessors/*

Sometimes, a path will generate more than one path because it can be
interpreted in different way::

	    //subjects//assessors//files

Generates::

	/projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*
	/projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*
	/projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*

.. warning::
    If you try ``//files``, it will generate all the possible descendant paths:

    | /projects/*/subjects/*/experiments/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/reconstructions/*/in_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/scans/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*
    | /projects/*/subjects/*/resources/*/files/*
    | /projects/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/reconstructions/*/out_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*

    If the server has decent amount a data it will take ages to go through all the resources.


Resources operations
--------------------

Several operations are accessible for every resource level. The most
importants are responsible for creating new resources, deleting
existing ones and testing whether a given resource exists or not::

    >>> my_project = central.select.project('my_project')
    >>> my_project.exists()
    False
    >>> my_project.create()
    >>> my_project.exists()
    True
    >>> subject = my_project.subject('first_subject')
    >>> subject.create()
    >>> subject.delete()
    >>> subject.exists()
    False

An optional keyword argument is available to specify the datatype from
the XNAT schema. The keyword must match the name of the REST level.

    >>> subject.create()
    >>> subject.experiment('pet_session'
              ).create(experiments='xnat:petSessionData')

It is also possible to create resources without having to create the
parent resources first. For example::

    >>> central.select('/project/PROJECT/subject/SUBJECT').exists()
    False
    >>> central.select('/project/PROJECT/subject/SUBJECT/experiment/EXP').exists()
    False

Specifiy the datatype on multiple levels::

    >>> central.select('/project/PROJECT/subject/SUBJECT/experiment/EXP/scan/SCAN'
                      ).create(experiments='xnat:mrSessionData', scans='xnat:mrScanData')

Use default datatypes::

    >>> central.select('/project/PROJECT/subject/SUBJECT/experiment/EXP/scan/SCAN'
                      ).create()


Additional fields can be configured at the resource creation. It can
be especially useful for datatypes that have some mandatory fields,
and thus would not be created if not specified (this is not a best
practice for XML Schema writers though). It also enables users to set
the resource ID through the REST API instead of just the label (the ID
in this case is generated automatically).

Custom ID example::

    >>> experiment.create(experiments='xnat:mrSessionData', 
                          ID='my_custom_ID'
                         ) 

With additional fields::

    >>> experiment.create(**{'experiments':'xnat:mrSessionData', 
                             'ID':'mr_custom_ID', 
			     'xnat:mrSessionData/age':'42'}
			  ) 

.. warning:: When using xpath syntax to declare fields, it is
	mandatory to pass the arguments using a dictionnary because of
	the ``/`` and ``:`` characters. And do not forget to expand
	the dict with the ``**``.

Since you can create different resource levels in a single create call
in pyxnat, it is also possible to configure those levels in a single
call. For example if the subject for that experiment was not created,
you could have specified::

    >>> experiment.create(
		**{'experiments':'xnat:mrSessionData', 
                   'ID':'mr_custom_ID',
                   'xnat:mrSessionData/age':'42', 
                   'xnat:subjectData/investigator/lastname':'doe', 
	           'xnat:subjectData/investigator/firstname':'john',
	           'xnat:subjectData/ID':'subj_custom_ID'
		  })
			  

File support
------------

It is possible to upload and then download files at every REST resource level::

    >>> my_project.files()
    []
    >>> my_project.file('image.nii').put('/tmp/image.nii')
    >>> # you can add any of the following arguments to give additional 
    >>> # information on the file you are uploading
    >>> my_project.file('image.nii').put( '/tmp/image.nii', 
                                          content='T1', 
                                          format='NIFTI'
                                          tags='image test'
                                        )
    >>> my_project.resource('NIFTI').file('image.nii').size()
    98098
    >>> my_project.resource('NIFTI').file('image.nii').content()
    'T1'
    >>> my_project.resource('NIFTI').file('image.nii').format()
    'NIFTI'
    >>> my_project.resource('NIFTI').file('image.nii').tags()
    'image test'
    >>> my_project.resource('NIFTI').file('image.nii').get()
    '~/.store/nosetests@central.xnat.org/c7a5b961fc504ffc9aa292f76d75fb0c_image.nii'
    >>> my_project.file('image.nii').get_copy()
    '~/.store/nosetests@central.xnat.org/workspace/projects/Volatile/resources/123150742/files/image.nii'
    >>> my_project.file('image.nii').get_copy('/tmp/test.nii')
    '/tmp/test.nii'
    >>> # the resource level can be used to group files
    >>> my_project.resource('ANALYZE').file('image.hdr').put('/tmp/image.hdr')
    >>> my_project.resource('ANALYZE').file('image.img').put('/tmp/image.img')
    >>> my_project.resources()
    ['NIFTI', 'ANALYZE']
    >>> my_project.resource('ANALYZE').files()
    ['image.hdr', 'image.img']

.. tip::
   New since 0.7, the default ``get()`` method on a file can be given
   a custom path. It will still be handled and tracked by the cache in
   the same way as other files.


Attributes support
------------------

Each resource level also has a set of metadata fields that can be
informed. This set of fields depends on the resource level and on its
type in the XNAT schema.

    >>> # use hard-coded shortcuts from the REST API
    >>> my_project.attrs.set('secondary_ID', 'myproject')
    >>> my_project.attrs.get('secondary_ID')
    'myproject'
    >>> # use XPATH from standard or custom XNAT Schema
    >>> my_project.attrs.set('xnat:projectData/keywords', 'test project')
    >>> my_project.attrs.get('xnat:projectData/keywords')
    'test project'
    >>> # get or set multiple attributes in a single request to improve performance
    >>> my_project.attrs.mset({'xnat:projectData/keywords':'test project', 'secondary_ID':'myproject'})
    >>> my_project.attrs.mget(['xnat:projectData/keywords', 'secondary_ID'])
    ['test porject', 'myproject']

_____

.. [#] http://www.xnat.org/XNAT+REST+XML+Path+Shortcuts
    

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
    >>> interface.select('//experiments').where(contraints)
    >>> # retrieve table with one subject per row and the columns SUBJECT_ID and AGE
    >>> interface.select('xnat:subjectData', ['xnat:subjectData/SUBJECT_ID', 'xnat:subjectData/AGE']).where(contraints)

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
       >>> interface.select('xnat:subjectData', 
       	   			['xnat:subjectData/SUBJECT_ID', 
       		                 'xnat:subjectData/AGE']).all()

.. tip:: 
   How to get all the columns from a datatype?
       >>> table = interface.select('xnat:subjectData').where(...)

.. tip:: 
   Then to get everything:
   	>>> table = interface.select('xnat:subjectData').all()
