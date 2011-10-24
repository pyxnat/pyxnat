Working with attributes
-----------------------

XNAT defines its data model, i.e. its data types and their relations
in an XML Schema. The elements stored in the database follow this
specification which can be used to get and set a range of attributes.
The only way to know all the attributes is to look at the relevant
schemas. The schemas are found on the XNAT server instances: e.g. 
https://central.xnat.org/schemas/xnat/xnat.xsd XNAT provides some
documentation on the attributes here: 
http://docs.xnat.org/XNAT+REST+XML+Path+Shortcuts
The attributes interface in **pyxnat** follows the same syntax.

Predefined shortcuts:

.. code-block:: python

    >>> project.attrs.set('secondary_ID', 'myproject')
    >>> project.attrs.get('secondary_ID')
    'myproject'

Generic, xpath-like syntax:

.. code-block:: python

    >>> project.attrs.set('xnat:projectData/keywords', 'test project')
    >>> project.attrs.get('xnat:projectData/keywords')
    'test project'

Get or set variables in a single call for optimal performance:


.. code-block:: python

    >>> project.attrs.mset({'xnat:projectData/keywords':'test project', 
    ...			    'secondary_ID':'myproject'
    ...			    })
    >>> project.attrs.mget(['xnat:projectData/keywords', 'secondary_ID'])
    ['test project', 'myproject']
