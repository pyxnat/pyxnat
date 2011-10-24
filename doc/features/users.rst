User Manager
------------

The REST API currently offers a limited number of functionalities to
manage users. It will be improved in future releases. The class 
:class:`~pyxnat.Interface.manage.users` contains methods to retrieve
information on the users registered on the server.

To list all the users:

.. code-block:: python

   >>> central.interface.manage.users()

To get information on a specific user:

.. code-block:: python

   >>> central.interface.manage.users.firstname('username')
   >>> central.interface.manage.users.lastname('username')
   >>> central.interface.manage.users.id('username')
   >>> central.interface.manage.users.email('username')

.. note:: In the future, it will be possible to create and delete users
   on an XNAT instance from the REST API. To add users to a project
   with a role see the documentation on the permission model of XNAT.
