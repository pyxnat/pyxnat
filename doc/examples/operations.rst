Resources Operations
--------------------

Common operations for :class:`~pyxnat.EObject` objects include creation,
deletion and existence checking.

.. code-block:: python

    >>> project = central.select.project('my_project')
    >>> project.exists()
    False
    >>> project.insert()
    >>> project.exists()
    True
    >>> subject = project.subject('first_subject')
    >>> subject.insert()
    >>> subject.delete()
    >>> subject.exists()
    False

.. note:: previous versions of **pyxnat** documentation mentionned 
:func:`~pyxnat.EObject.create` instead of :func:`~pyxnat.EObject.insert` to
create new resources. :func:`~pyxnat.EObject.create` still exists and
will probably never be deprecated. However :func:`~pyxnat.EObject.insert`
is now preferred since most **pyxnat** operations try to borrow vocabulary
from SQL.

REST resources are given a default type when they are created but it's
possible to customize it with a type defined in the XNAT XML Schema(s).

.. code-block:: python

    >>> experiment.insert(experiments='xnat:petSessionData')
    >>> scan.insert(scans='xnat:petScanData')

It is also possible to create resources without having to create the
parent resources first. For example:

.. code-block:: python

    >>> subject = central.select('/project/PROJECT/subject/SUBJECT')
    >>> subject.exists()
    False
    >>> experiment = subject.experiment('EXP')
    >>> experiment.exists()
    False    
    >>> experiment.insert()
    >>> subject.exists()
    True
    >>> experiment.exists()
    True    

Specifiy the datatype on multiple elements in a single statement:

.. code-block:: python

    >>> scan = central.select('/project/PROJECT/subject/SUBJECT/experiment/EXP/scan/SCAN'
    >>> scan.insert(experiments='xnat:mrSessionData', scans='xnat:mrScanData')

Additional fields can be configured at the resource creation. It can
be especially useful for datatypes that have some mandatory fields,
and thus would not be created if not specified (this is not a best
practice for XML Schema writers though). It also enables users to set
the resource ID through the REST API instead of just the label (the ID
in this case is generated automatically).

Custom ID example:

.. code-block:: python

    >>> experiment.create(experiments='xnat:mrSessionData', 
                          ID='my_custom_ID'
                         ) 

With additional fields:

.. code-block:: python

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
