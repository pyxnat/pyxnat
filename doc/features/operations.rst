Operating the database
----------------------

Basic operations
~~~~~~~~~~~~~~~~

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
   :func:`~pyxnat.EObject.create` instead of :func:`~pyxnat.EObject.insert`
   to create new resources. :func:`~pyxnat.EObject.create` still exists and
   will probably never be deprecated.

Custom datatypes
~~~~~~~~~~~~~~~~

REST resources are given a default type when they are created but it is
possible to customize it with a type defined in the XNAT XML Schema(s).

.. code-block:: python

    >>> experiment.insert(experiments='xnat:petSessionData')
    >>> scan.insert(scans='xnat:petScanData')

Multiple creation
~~~~~~~~~~~~~~~~~

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

Additional data at creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Additional fields can be configured at the resource creation. It can
be especially useful for datatypes that have some mandatory fields,
and thus would not be created if not specified (this is not a best
practice for XML Schema writers though). It also enables users to set
the resource ID through the REST API instead of just the label (the ID
in this case is generated automatically).

Custom ID example:

.. code-block:: python

    >>> experiment.insert(experiments='xnat:mrSessionData',
                          ID='my_custom_ID'
                          )

With additional fields:

.. code-block:: python

    >>> experiment.insert(**{'experiments':'xnat:mrSessionData',
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
you could have specified:

.. code-block:: python

    >>> experiment.insert(
    ...		**{'experiments':'xnat:mrSessionData',
    ...            'ID':'mr_custom_ID',
    ...            'xnat:mrSessionData/age':'42',
    ...            'xnat:subjectData/investigator/lastname':'doe',
    ...	           'xnat:subjectData/investigator/firstname':'john',
    ...	           'xnat:subjectData/ID':'subj_custom_ID'
    ...		  })
