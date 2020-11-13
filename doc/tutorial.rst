:orphan:

.. module:: pyxnat

Getting started
===============

This tutorial is intended as an introduction on how to work with
**XNAT** and :mod:`pyxnat`. Reading the `XNAT documentation
<http://docs.xnat.org/>`_, especially on the pages on the REST
Web Services, can be a huge help to deeper understand
**XNAT** and consequently :mod:`pyxnat` design decisions.

Prerequisites
-------------
Before starting, make sure that you have the :mod:`pyxnat` distribution
:doc:`installed <installing>`. In the Python shell, the following
should run without raising an exception:

.. code-block:: python

  >>> import pyxnat

This tutorial also assumes that you have access to an XNAT instance.
You may also use `XNAT Central <https://central.xnat.org>`_, which is a public
instance managed by the XNAT team and updated on a regular basis.

Setting up a connection
-----------------------

The first step when working with :mod:`pyxnat` is to connect to an XNAT
instance with :class:`~pyxnat.Interface`. For this, you will need valid
credentials. Make sure you have them or request them through the web interface
of the targeted host.

.. code-block:: python

   >>> from pyxnat import Interface
   >>> central = Interface(server="https://central.xnat.org",
   ...			   user='my_login',
   ...		     password='my_pass')


.. warning::
    Depending on the server configuration, you may have to include the port
    in the server URL, as well as the name of the XNAT `tomcat` application.
    You might end up with something like:
    `http://server_ip:port/xnat`

Alternative connections
~~~~~~~~~~~~~~~~~~~~~~~

If at least one of server, user and password arguments is missing,
the user will be prompted for it (them). In this mode, a connection
to the server will be attempted at the object creation and will raise
an exception if something is wrong.

.. code-block:: python

   >>> central = Interface(server="https://central.xnat.org")
       User:my_login
       Password:

There are two types of configuration files that :mod:`pyxnat` uses.
The first one is used with the `config` parameter.

.. code-block:: python

   >>> central = Interface(config='central.cfg')

The easiest way to create this configuration file is to use the
:func:`~pyxnat.Interface.save_config()` method on an existing interface.

.. code-block:: python

   >>> central.save_config('central.cfg')

The second one is the XNAT format config file, which is placed at a
default location (i.e. `~/.xnatPass` in Linux). It is used without passing
any argument to the :class:`~pyxnat.Interface` object. It is formatted
as follows and supports multiple accounts and servers, the active one
being the one selected by a ``+`` sign:

.. code-block:: none

   +loginone@http://central.xnat.org=password
   -logintwo@http://central.xnat.org=password
   -logintwo@http://localhost=password

.. code-block:: python

   >>> central = Interface()

.. note:: If :class:`~pyxnat.Interface` is used without any parameter
   and any configuration file at default location,
   user will be prompted for server, user and password.

.. warning::
  You may prefer not to have your password either displayed onscreen or embedded
  in your programs. Two alternatives for interactive sessions and scripts: if
  you omit any of these three required parameters, the call to Interface(.) will
  prompt for the missing ones, and will not display the password as you enter it
  from the keyboard. Alternately, you can prompt for the password in the same
  way by using Python's getpass.getpass(.) method, some variations of which are
  demonstrated in examples below.

  You can save an entire configuration to a file and then load it later.
  Note that the configuration file contains the password, so be sure only to
  save this file in an access-protected location.

Traversing the database
-----------------------

Traversing the database requires basic knowledge of XNAT data model.
This information is available in the
:func:`~pyxnat.Interface.inspect.structure` method of the
:class:`~pyxnat.Interface.inspect` sub-interface, which prints the
hierarchical organization of the data and helps constructing valid
``paths`` for accessing the data. The :class:`~pyxnat.Interface.select`
sub-interface allows for data selection and basic filtering through
Python objects or ``paths``, more akin to native REST calls.

Simple requests::

    >>> central.select.projects().get()
    [..., 'CENTRAL_OASIS_CS', 'CENTRAL_OASIS_LONG', ...]
    >>> central.select('/projects').get()
    [..., 'CENTRAL_OASIS_CS', 'CENTRAL_OASIS_LONG', ...]

Nested requests::

    >>> central.select.projects().subjects().get()
    >>> central.select('/projects/*/subjects').get()
    >>> central.select('/projects/subjects').get()
    >>> central.select('//subjects').get()
    ['IMAGEN_000000001274', 'IMAGEN_000000075717', ...,'IMAGEN_000099954902']

Filtered requests::

    >>> central.select.projects('*OASIS_CS*').get()
    >>> central.select('/projects/*OASIS_CS*').get()
    ['CENTRAL_OASIS_CS']

    >>> central.select.project('IMAGEN').subjects('*55*42*').get()
    >>> central.select('/projects/IMAGEN/subjects/*55*42*').get()
    ['IMAGEN_000055203542', 'IMAGEN_000055982442', 'IMAGEN_000097555742']

Operating the database
----------------------

Python resource Objects that are retrieved from the
:class:`~pyxnat.Interface.select` interface support a range of
operations to interact and insert data in **XNAT**.
:class:`~pyxnat.EObject` objects support operations for creation, deletion
and existence checking.


.. code-block:: python

   >>> subject.insert()
   >>> subject.exists()
   True
   >>> subject.delete()
   >>> subject.exists()
   False

Working with Files
~~~~~~~~~~~~~~~~~~

**XNAT** was built to store images which means it can handle files.
Files resources in :mod:`pyxnat`
are just :class:`~pyxnat.EObject` objects with a few additional
methods to upload and download the data.

.. code-block:: python

   >>> file.get()
   '<cachedir>/hash_of_file_uri.extension'
   >>> file.get('/tmp/image.nii')
   '/tmp/image.nii'
   >>> file.put('/tmp/modified_image.nii')
