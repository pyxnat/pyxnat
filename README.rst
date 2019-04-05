.. image:: https://img.shields.io/travis/pyxnat/pyxnat.svg
    :target: https://travis-ci.org/pyxnat/pyxnat
.. image:: https://coveralls.io/repos/github/pyxnat/pyxnat/badge.svg?branch=master
    :target: https://coveralls.io/github/pyxnat/pyxnat?branch=master
.. image:: https://img.shields.io/pypi/dm/pyxnat.svg
    :target: https://pypi.org/project/pyxnat/
.. image:: https://img.shields.io/pypi/pyversions/pyxnat.svg
    :target: https://pypi.org/project/pyxnat
.. image:: https://img.shields.io/pypi/v/pyxnat.svg
    :target: https://pypi.org/project/pyxnat

The homepage of pyxnat with user documentation is located on:

http://packages.python.org/pyxnat/

Getting the latest code
=========================

To get the latest code using git, simply type::

    git clone git://github.com/pyxnat/pyxnat.git

If you don't have git installed, you can download a zip or tarball
of the latest code: http://github.com/pyxnat/pyxnat/archives/master

Or the lastest stable version: http://pypi.python.org/pypi/pyxnat

Installing
=========================

As any Python packages, to install pyxnat, simply do::

    python setup.py install

in the source code directory.

Workflow to contribute
=========================

To contribute to pyxnat, first create an account on `github
<http://github.com/>`_. Once this is done, fork the `pyxnat repository
<http://github.com/pyxnat/pyxnat>`_ to have you own repository,
clone it using 'git clone' on the computers where you want to work. Make
your changes in your clone, push them to your github account, test them
on several computer, and when you are happy with them, send a pull
request to the main repository.

Running the test suite
=========================

To run the test suite, you need nosetests and the coverage modules.
Run the test suite using::

    nosetests

from the root of the project.


Building the docs
=========================

To build the docs you need to have setuptools and sphinx (>=0.5) installed.
Run the command::

    python setup.py build_sphinx

The docs are built in the build/sphinx/html directory.


Making a source tarball
=========================

To create a source tarball, eg for packaging or distributing, run the
following command::

    python setup.py sdist

The tarball will be created in the `dist` directory. This command will
compile the docs, and the resulting tarball can be installed with
no extra dependencies than the Python standard library. You will need
setuptool and sphinx.

Making a release and uploading it to PyPI
==================================================

This command is only run by project manager, to make a release, and
upload in to PyPI::

    python setup.py sdist bdist_egg register upload

Licensing
----------

pyxnat is **BSD-licenced** (3 clause):

    This software is OSI Certified Open Source Software.
    OSI Certified is a certification mark of the Open Source Initiative.

    Copyright (c) 2010-2011, Yannick Schwartz
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

    * Neither the name of Yannick Schwartz. nor the names of other pyxnat
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

    **This software is provided by the copyright holders and contributors
    "as is" and any express or implied warranties, including, but not
    limited to, the implied warranties of merchantability and fitness for
    a particular purpose are disclaimed. In no event shall the copyright
    owner or contributors be liable for any direct, indirect, incidental,
    special, exemplary, or consequential damages (including, but not
    limited to, procurement of substitute goods or services; loss of use,
    data, or profits; or business interruption) however caused and on any
    theory of liability, whether in contract, strict liability, or tort
    (including negligence or otherwise) arising in any way out of the use
    of this software, even if advised of the possibility of such
    damage.**
