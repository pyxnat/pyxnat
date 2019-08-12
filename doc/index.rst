.. pyxnat documentation master file, created by sphinx-quickstart on Tue Nov 24 11:04:02 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. module:: pyxnat

pyxnat: XNAT in Python
======================

**Date**: |today| **Version**: |version|

**Useful links**:
`Binary Installers <https://pypi.org/project/pyxnat>`__ |
`Source Repository <https://github.com/pyxnat/pyxnat>`__ |
`Issues & Ideas <https://github.com/pyxnat/pyxnat/issues>`__


Overview
--------

:mod:`pyxnat` is an open source, BSD-licenced library providing a programmatic
interface with `XNAT <http://www.xnat.org>`_ which is an extensible management system
for imaging data (and related). :mod:`pyxnat` uses the RESTful Web services
provided by XNAT and allows easier interaction with an XNAT server through a
simple and consistent API using the `Python <https://www.python.org/>`_
programming language.


* :doc:`installing`
* :doc:`tutorial`
* :doc:`starters_tutorial`
* :doc:`advanced_tutorial`
* :doc:`features/index`
* :doc:`reference_documentation`
* :doc:`external_resources`
* :doc:`about`
* :doc:`CHANGES`


Short examples
""""""""""""""

**Setup a connection**

.. code-block:: python

   >>> from pyxnat import Interface
   >>> interface = Interface(server='https://central.xnat.org',
                             user='login',
                             password='pass')

**Traverse the resource tree**

.. code-block:: python

   >>> list(interface.select.projects())
   ['CENTRAL_OASIS_CS', 'CENTRAL_OASIS_LONG', ...]

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
    Interface
    Select
    SearchManager
    Users
