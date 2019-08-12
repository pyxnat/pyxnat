=======
pyxnat
=======

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


Where to get it
===============

The source code is currently hosted on GitHub at:
https://github.com/pyxnat/pyxnat

Binary installers for the latest released version are available at the `Python
package index <https://pypi.org/project/pyxnat>`_. **pyxnat** can be installed
using ``pip`` with the following command::

    pip install pyxnat

Dependencies
============

- `requests <https://2.python-requests.org/en/master/>`_ v2.20 or higher
- `python-lxml <https://lxml.de/>`_ v4.3.2 or higher recommended, earlier versions may work.

For development purposes:

- *python-nose* v1.2.1 or higher
- *coverage* v3.6 or higher

See the `full installation instructions <https://pyxnat.github.io/pyxnat/installing.html>`_
for recommended and optional dependencies.

Installation from sources
=========================

To install **pyxnat** from source, from the ``pyxnat`` directory (same one
where you found this file after cloning the git repo), execute::

    python setup.py install


Documentation
=============

The official documentation is hosted at: https://pyxnat.github.io/pyxnat

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


Building the documentation
==========================

Building the docs requires to have `setuptools <https://pypi.org/project/setuptools/>`_
and `sphinx <http://www.sphinx-doc.org/en/master/>`_ (v2.0+) installed.
Then run the command::

    python setup.py build_sphinx

The docs are built in the ``build/sphinx/html`` folder.

Contribute to **pyxnat**
=========================

To contribute to **pyxnat**, first create an account on `GitHub
<http://github.com/>`_. Once this is done, fork the `pyxnat repository
<http://github.com/pyxnat/pyxnat>`_ to have you own repository,
clone it using ``git clone`` on the computers where you want to work. Make
changes in your clone, push them to your GitHub fork, test them
on several computers and when you are happy with them, send a `pull
request <https://github.com/pyxnat/pyxnat/issues>`_ to the main repository.

License
=======

`BSD 3 <LICENSE>`_
