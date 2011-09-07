More on Paths
-------------

The ``paths`` which are passed as arguments to 
:class:`~pyxnat.Interface.select` can take different forms. They are
in fact compatible with native REST calls, except for query strings in
the URLs (see `XNAT doc <http://docs.xnat.org/XNAT+REST+API+Usage>`_
and `Wikipedia <http://en.wikipedia.org/wiki/Query_string>`_ for more on
query strings). They also expose additional functionalities and can 
easily generate thousands of queries in a single statement.

Absolute Paths
~~~~~~~~~~~~~~

A full path to a resource is a sequence of resource level and
resource_id pairs, whereas a full path to a resource listing is
a sequence of resource level and resource_id pairs finishing by a 
plural resource level (i.e. with an 's')

.. code-block:: python

   >>> central.select('/project/IMAGEN/subject/000055982442')
   >>> central.select('/project/IMAGEN/subject/000055982442/experiments')

The :class:`~pyxnat.Interface.select` statement is smart enough to deal
with `plural` and `singluar` resources names which means that the
following ``paths`` are equivalent in **pyxnat**.

.. code-block:: python

   >>> central.select('/project/IMAGEN/subject/000055982442/experiments')
   >>> central.select('/project/IMAGEN/subjects/000055982442/experiment')
	 
Relative Paths and Shortcuts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When browsing resources, some levels are often left without any IDs
and filled with ``*`` filters instead, which leads to paths like.

.. code-block:: python

   >>> central.select('/projects/*/subjects/*/experiments/*')

**pyxnat** offers shorter ways to do it. There are intended to explore
faster the database from an interactive python shell such as `ipython
<http://ipython.org/>`_, but not in production programs where using
Python string replacement capabilities to generate identifiers is 
always faster. The previous statement is equivalent to the following calls:

.. code-block:: python

   >>> central.select('/projects/subjects/experiments')
   >>> central.select('//experiments')

Another example to get all the experiments from a specific project.

.. code-block:: python

   >>> central.select('/project/IMAGEN//experiments')
   >>> central.select('/project/IMAGEN/subjects/*/experiments')
   
The double slash syntax can be used anywhere in the path and any
number of time to avoid writing unused `levels` in the ``path``.

.. code-block:: python

   >>> central.select('//subjects//assessors')
   >>> central.select('/projects/*/subjects/*/experiments/*/assessors/*')

A ``path`` will generate several ``paths`` and thus several queries if
it's ambiguous and can be interpreted in differents ways. For example the
path ``//subjects//assessors//files`` generates:

.. code-block:: python
	    
    /projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*
    /projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*
    /projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*

.. warning:: If you try ``//files``, it will generate all the possible
   descendant paths. If the server has a large amount a data it will 
   take ages to go through all the resources:

    | /projects/*/subjects/*/experiments/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/reconstructions/*/in_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/scans/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*
    | /projects/*/subjects/*/resources/*/files/*
    | /projects/*/resources/*/files/*
    | /projects/*/subjects/*/experiments/*/reconstructions/*/out_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*
    | /projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*
