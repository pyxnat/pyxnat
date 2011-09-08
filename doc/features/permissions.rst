Permission Model
----------------

Project Configuration
~~~~~~~~~~~~~~~~~~~~~

XNAT permission model uses a number of methods. The first thing is 
the project accessibility. A project can be private, protected or 
public. A private project is visible only by its users, a protected project
is only accessible by its users and a public project is accessible by
everyone.

.. code-block:: python

   >>> central.select('/project/PROJ').set_accessibility('public')
   >>> central.select('/project/PROJ').accessibility()
   'public'

The second thing is user roles within a project. Users can be owners, 
members or collaborators to give read or write access to projects:

.. code-block:: python

   >>> central.select('/project/PROJ').add_user('my_friend', 'member')
   >>> central.select('/project/PROJ').add_user('my_other_friend', 'owner')

Resource Sharing
~~~~~~~~~~~~~~~~

The last thing is the ability to share subjects, experiments and assessors
accross projects. Subjects shared to a private project enables a user to
add experiments, or processing results to the subject which would not have
been possible if the user didn't have write access to the original project.
This functionality is also used to share a subject which is scanned across
multiple studies, but restrain access of its data to the relevant 
investigators.

.. code-block:: python

    >>> subject = interface.select('/project/project1/subject/subject1')
    >>> subject.share('project2')
    >>> subject.unshare('project2')
    >>> # to know to in which projects a subject is available
    >>> subject.shares()

Almost the same interface is available for collection objects:

.. code-block:: python

    >>> subjects = interface.select('/project/project1/subjects')
    >>> subjects.share('project2')
    >>> subjects.unshare('project2')
    >>> # to retrieve the subjects sharing a list of projects
    >>> subjects.sharing(['project1', 'project2'])

.. note::
    Of course the permissions policies (user level and project
    accessibility) still apply.

.. warning::
    The ``shares`` and ``sharing`` methods are not implemented in an
    efficient way at the moment. There is another more concerning
    issue: subjects for example are accessible through their ID or
    label. But labels stop working when trying to access a subject
    through a project that is not its orginial one.

