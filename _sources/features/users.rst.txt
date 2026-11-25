User Manager
------------

The REST API currently offers a limited number of features to
manage users. The class :class:`~pyxnat.Interface.manage.users` may be used to
know about registered users on the server.

To list all existing users:

.. code-block:: python

   >>> central.interface.manage.users()

On a specific user:

.. code-block:: python

   >>> central.interface.manage.users.firstname('username')
   >>> central.interface.manage.users.lastname('username')
   >>> central.interface.manage.users.id('username')
   >>> central.interface.manage.users.email('username')

To assign users with specific roles (owner/member/collaborator) in a project:

.. code-block:: python

   >>> central.select.project('project').add_user('admin', 'collaborator')
