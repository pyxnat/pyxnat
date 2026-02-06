Provenance
----------

XNAT offers some support for provenance. Provenance is the description of
processing steps that a particular data went through to be created. While
all the complexity of a processing workflow cannot be represented at the
moment, it provides sufficient information to have a good idea of what
the data is. Reconstructions and assessors are the only level that support
provenance in XNAT.

.. code-block:: python

    >>> prov = {'program':'young',
    ...         'timestamp':'2011-03-01T12:01:01.897987', 
    ...         'user':'angus', 
    ...         'machine':'war', 
    ...         'platform':'linux',
    ...        }
    >>> element.provenance.set(prov)
    >>> element.provenance.get()
    >>> element.delete()

.. warning:: The `delete` method doesn't work currently.

The provenance ``set`` method adds new steps with each call, unless the 
overwrite parameter is set to True. The following keywords for the 
provenance dictionnay are available:

    - program
    - program_version
    - program_arguments
    - timestamp
    - cvs
    - user
    - machine
    - platform
    - platform_version
    - compiler
    - compiler_version
