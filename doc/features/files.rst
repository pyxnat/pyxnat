Working with Files
------------------

Files, containing images or other data are attached to elements with URIs
defining a ``resource`` level and a ``file`` level:

.. code-block:: python

    >>> project.resources().files()
    ['image.nii']

Upload Files
~~~~~~~~~~~~

Files are uploaded with the :func:`~pyxnat.File.insert` method, which
is similar to the :func:`~pyxnat.EObject.insert` method but supports
different arguments:

.. code-block:: python

    >>> project.resource('NIFTI').file('T1.nii').insert('/tmp/image.nii')
    >>> project.resource('NIFTI').file('image.nii').insert(
    ...		'/tmp/image.nii', 
    ...		content='T1', 
    ...		format='NIFTI'
    ...		tags='image test')

.. note:: The old :func:`~pyxnat.File.put` method is equivalent to
   :func:`~pyxnat.File.insert` and is still working.

.. warning:: The `content`, `format` and `tags` attributes can only
   be set when uploading the file, and then cannot be modified.

Download Files
~~~~~~~~~~~~~~

Files are downloaded with the :func:`~pyxnat.File.get` method. Given no
location, a default path in the cachedir will be automatically generated
and returned. A custom location can however be given and the file will
still be tracked by the :class:`~pyxnat.CacheManager` and affected by its
operations. Use :func:`~pyxnat.File.get_copy` instead if you want to
download a file outside of the cache scope.

.. note:: :func:`~pyxnat.File.get_copy` does what it says, it copies the 
   file, so you'll have one version in the cache and one version at the
   requested location.

.. code-block:: python

    >>> project.resource('NIFTI').file('T1.nii').get()
    '/tmp/nosetests@central.xnat.org/c7a5b961fc504ffc9aa292f76d75fb0c_image.nii'
    >>> project.resource('NIFTI').file('T1.nii').get('/tmp/test.nii')
    '/tmp/test.nii'
    >>> project.resource('NIFTI').file('T1.nii').get_copy()
    '/tmp/nosetests@central.xnat.org/workspace/projects/Volatile/resources/123150742/files/image.nii'
    >>> project.resource('NIFTI').file('T1.nii').get_copy('/tmp/test.nii')
    '/tmp/test.nii'

Get attributes
~~~~~~~~~~~~~~

If attributes were defined they can be retrieved:

.. code-block:: python

    >>> project.resource('NIFTI').file('image.nii').size()
    98098
    >>> project.resource('NIFTI').file('image.nii').content()
    'T1'
    >>> project.resource('NIFTI').file('image.nii').format()
    'NIFTI'
    >>> project.resource('NIFTI').file('image.nii').tags()
    'image test'
