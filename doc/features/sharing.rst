Sharing
-------

Sharing may be a misleading name because it is actually part of
the permission system in XNAT.

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
