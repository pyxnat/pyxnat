====================
Under the Hood
====================

The REST model
--------------

Check out the wikipedia page if you are not familiar with REST.

_____

.. [#] http://en.wikipedia.org/wiki/REST

The REST model in XNAT
----------------------

Basically the resources are accessible pairing a level and its ID in a sequence
representing a URI starting by /REST.

Uniquely identifiable resources:
    - /REST/projects/{ID}
    - /REST/projects/{ID}/subjects/{ID}

Listing the resources is done by not giving an ID at the end of a URI:
    - /REST/projects
    - /REST/projects/{ID}/subjects

Requesting specific data in specific format is done with a query string:
    - /REST/projects?format=csv
    - /REST/projects/{ID}?format=xml

_____

.. [#] http://www.xnat.org/Web+Services

REST in Python
--------------

The REST resource levels supported by this Python library are the following::
  
  - projects
      - subjects
          - experiments
              - scans
              - reconstructions
              - assessors


Attached to each resource level are::

  - resources
      - files

Every level corresponds to a Python class sharing common methods from
ResourceObject and adding methods relevant to the specific resource.

        +-----------------+----------------+
        | REST resource   | Python Class   |
        +=================+================+
        | REST            | Interface      |
        +-----------------+----------------+
        | projects        | Project        |
        +-----------------+----------------+
        | subjects        | Subject        |
        +-----------------+----------------+
        | experiments     | Experiment     | 
        +-----------------+----------------+
        | scans           | Scan           | 
        +-----------------+----------------+
        | reconstructions | Reconstruction | 
        +-----------------+----------------+
        | assessors       | Assessor       |
        +-----------------+----------------+
        | resources       | Resource       | 
        +-----------------+----------------+
        | files           | File           | 
        +-----------------+----------------+


This classes may but should not be instantiated manually.

The HTTP requests are handled by a slightly modified version of httplib2, which is 
shipped the package. The main fix was made to enable back the built-in HTTP cache
to avoid downloading again files that are already in the cache. This changes nothing
for other resources that don't have to necessary HTTP headers to enable a cache service.



