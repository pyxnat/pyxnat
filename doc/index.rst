.. pyxnat documentation master file, created by sphinx-quickstart on Tue Nov 24 11:04:02 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

pyxnat: XNAT in Python
======================

Overview
--------

:mod:`pyxnat` is an open source, BSD-licenced library providing a programmatic
interface with `XNAT <http://www.xnat.org>`_ which is an extensible management system
for imaging data (and related). :mod:`pyxnat` uses the RESTful Web services
provided by XNAT and allows easier interaction with an XNAT server through a
simple and consistent API using the `Python <https://www.python.org/>`_
programming language.

:doc:`installing`
	Instructions on how to get the distribution.

:doc:`tutorial`
	Start here for a quick overview.

:doc:`features/index`
	Detailed documentation and examples.

:doc:`external_resources`
	References to related projects and external resources.

:doc:`about`
	Contributors and funding.

:doc:`CHANGES`
	See changes from the latest version.

Links
"""""

#. Documentation: http://packages.python.org/pyxnat/
#. Download: http://pypi.python.org/pypi/pyxnat#downloads
#. Sources: http://github.com/pyxnat/pyxnat

Short examples
""""""""""""""

**Setup the connection**

.. code-block:: python

   >>> from pyxnat import Interface
   >>> interface = Interface(
       		 server='https://central.xnat.org',
                 user='login',
                 password='pass',
                 cachedir='/tmp'
                 )

**Traverse the resource tree**

.. code-block:: python

   >>> interface.select.projects().get()
   [u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]

**Operate the database**

.. code-block:: python

   >>> project = interface.select.project('my_project').insert()
   >>> project.resource('images').file('image.nii').insert('/tmp/image.nii')

**Use the search engine**

.. code-block:: python

   >>> table = interface.select(
       	       'xnat:subjectData',
	       ['xnat:subjectData/PROJECT', 'xnat:subjectData/SUBJECT_ID']
	       ).where([('xnat:subjectData/SUBJECT_ID','LIKE','%'),
                        ('xnat:subjectData/PROJECT', '=', 'my_project'),
                        'AND'
                        ])


Module contents
----------------

.. currentmodule :: pyxnat

.. autosummary::
   :toctree: generated/

    Interface
    Select
    SearchManager
    CacheManager
    Users
