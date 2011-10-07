Schema Manager
--------------

This manager is intented to provide a few helpers for those who wish to
explore the schema. This is useful to find paths that can be used to
get and set attributes for XNAT datatypes (see documentation on attributes).
However this helpers are far from perfect and do not provide all the paths,
and all the paths that are provided are not valid. Addictional documentation
on attributes paths is available here: 
http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts.

The first things to do when using this manager is to add a schema. There
is currently no way to guess the URLs of the schema so this is a manual
step. For example to add the core XNAT schema, the following calls are
equivalent:

.. code-block:: python

   >>> central.manage.schemas.add('xnat/xnat.xsd')
   >>> central.manage.schemas.add('xnat.xsd')

.. note:: it is better to use a full path to the schema, so the first call
   is preferred to the second.

To remove a schema from the manager:

.. code-block:: python

   >>> central.manage.schemas.remove('xnat.xsd')

You can look manually at the datatypes from schema using the
:func:`~pyxnat.inspect.schemas` methods, but the preferred way is to
call the :class:`~pyxnat.EObject.attrs` methods to list all the attributes
relevant to that element. If no schema was added to the manager, the 
returned list will be empty:

.. code-block:: python

   >>> element.attrs()

.. note:: This functionalities will eventually disapear, as it is part
   of the XNAT roadmap to provide REST services to query the schemas.


