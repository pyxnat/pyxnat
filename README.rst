=======
pyxnat
=======

..  image:: https://github.com/pyxnat/pyxnat/actions/workflows/ci.yml/badge.svg
     :target: https://github.com/pyxnat/pyxnat/actions/workflows/ci.yml
.. image:: https://coveralls.io/repos/github/pyxnat/pyxnat/badge.svg?branch=master
    :target: https://coveralls.io/github/pyxnat/pyxnat?branch=master
.. image:: https://img.shields.io/pypi/dm/pyxnat.svg
    :target: https://pypi.org/project/pyxnat/
.. image:: https://img.shields.io/pypi/pyversions/pyxnat.svg
    :target: https://pypi.org/project/pyxnat
.. image:: https://img.shields.io/pypi/v/pyxnat.svg
    :target: https://pypi.org/project/pyxnat

.. image:: https://gitlab.com/xgrg/tweetit/-/raw/master/resources/008-pyxnat-v1.4.gif?inline=false

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

- `requests <https://requests.readthedocs.io/>`_ v2.20 or higher
- `python-lxml <https://lxml.de/>`_ v4.3.2 or higher recommended, earlier versions may work.

For development purposes:

- `pytest <https://pytest.org/>`_ v7.1 or higher
- `coverage <https://coverage.readthedocs.io/>`_ v3.6 or higher

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
using a dedicated user account (``nosetests``). However, some tests could not run
due to restricted permissions. In v1.1, tests were restructured to use two
independent XNAT instances based on permission level.

A public XNAT instance (NITRC/IR) is used for most tests with read access, while
tests requiring write permissions run against a local XNAT instance in a Docker
container.

Running the test suite requires the following:

  - *pytest* v7.1+
  - *coverage* v3.6+
  - *docker* v18+

A local Docker-powered XNAT instance can be set up using ``docker-compose`` and
any available recipe. We recommend the one maintained by the XNAT
team (`xnat-docker-compose <https://github.com/NrgXnat/xnat-docker-compose>`_).
Once the repository is cloned, run::

  docker-compose up -d

After a couple of minutes, the XNAT instance should be up and running locally at
http://localhost.

Finally run the tests from the root of the project::

    pytest --cov pyxnat

See .github/workflows/ci.yml (used for CI) for the full test setup.


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
