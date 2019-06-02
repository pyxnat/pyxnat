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

The homepage of **pyxnat** with user documentation is located on:

https://pyxnat.readthedocs.io/en/latest/

Getting the latest code
=========================

To get the latest code using git, simply type::

    git clone git://github.com/pyxnat/pyxnat.git

You can download a zip or tarball
of the latest code: http://github.com/pyxnat/pyxnat/archives/master

Or the latest stable version: http://pypi.python.org/pypi/pyxnat

Installing
=========================

**pyxnat** can be installed via pip from
`PyPI <https://pypi.org/project/pyxnat>`__.

::

    pip install pyxnat


Or as any Python package, to install **pyxnat** from source code, simply do::

    python setup.py install

in the source code directory.

Contribute to **pyxnat**
=========================

To contribute to **pyxnat**, first create an account on `GitHub
<http://github.com/>`_. Once this is done, fork the `pyxnat repository
<http://github.com/pyxnat/pyxnat>`_ to have you own repository,
clone it using 'git clone' on the computers where you want to work. Make
changes in your clone, push them to your GitHub fork, test them
on several computers and when you are happy with them, send a `pull
request <https://github.com/pyxnat/pyxnat/issues>`_ to the main repository.

Running the test suite
=========================

Until v1.1 tests were exclusively performed on `XNAT Central <http://central.xnat.org>`_
using a dedicated user account (``nosetests``). Yet some tests were not allowed to
run due to restricted permissions.
In v1.1, tests were restructured and were directed to two independent XNAT
instances based on permission level. Hence `XNAT Central <http://central.xnat.org>`_
is still used for most tests with read access whereas other tests requiring
write permissions are run on a local XNAT instance in a Docker container.

Consequently, running the test suite now requires the following:
  - *python-nose* v1.2.1+
  - *coverage* v3.6+
  - *docker* v18+

Setting up a local Docker-powered XNAT instance may be achieved easily using
``docker-compose`` and any available recipe. We recommend the one from the
`following repository <https://github.com/NrgXnat/xnat-docker-compose>`_
(maintained by the XNAT team). Once the repository cloned, run the following
command (possibly as ``sudo``) ::

  docker-compose up -d

After a couple of minutes, the XNAT instance should be up and running locally.
You may check it out visiting http://localhost.

The script ``tests/setup_xnat.py`` may then be executed to populate the local
instance before running the tests.

Finally run the tests with the following command (from the root of the project)::

    nosetests pyxnat/tests

The file ``.travis.yml`` (used for CI) features these described steps and may be
referred to for further information.


Building the docs
=========================


 Building the docs requires to have `setuptools <https://pypi.org/project/setuptools/>`_
 and `sphinx <http://www.sphinx-doc.org/en/master/>`_ (v2.0+) installed.
You will also need the `numpydoc <https://pypi.org/project/numpydoc/>`_ package.
Then run the command::

    python setup.py build_sphinx

The docs are built in the ``build/sphinx/html`` folder.



Licensing
=========

**pyxnat** is **BSD-licenced** (3 clause):

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
