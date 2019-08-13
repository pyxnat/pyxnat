:orphan:

.. module:: pyxnat

Installation
============


Python version support
----------------------

Officially Python 2.7, 3.6, and 3.7.


Installing from PyPI
--------------------

:mod:`pyxnat` can be installed via pip from
`PyPI <https://pypi.org/project/pyxnat>`__.

::

    pip install pyxnat

Prerequisites
-------------

- *python* v2.7+
- `requests <https://2.python-requests.org/en/master/>`_ v2.20
- `python-lxml <https://lxml.de/>`_ v4.3.2+ recommended, earlier versions may work.

For development purposes:

- *python-nose* v1.2.1+ to run the unit tests
- *coverage* v3.6+


The manual way
---------------

To install :mod:`pyxnat`, first download the latest tarball (e.g. from
http://pypi.python.org/pypi/pyxnat) and expand it.

Installing in a local environment
..................................

If you do not need to install for all users, we strongly suggest that you
create a local environment and install :mod:`pyxnat` in it. One advantage of
this method is that you never have to become administrator and thus all
changes are local and easy to clean up.

    #. First, create the following directory (where `~` is the home folder,
       or any directory that you want to use as a base for
       your local Python environment, and `X` is your Python version
       number, e.g. `2.6`)::

	~/usr/lib/pythonX/site-packages

    #. Second, make sure that you add this directory in your environment
       variable `PYTHONPATH`. Windows users may do this by editing
       your environment variables in the system configuration dialog. Unix
       users may add the following line to their `.bashrc` or any file
       sourced at login::

	export PYTHONPATH=$HOME/usr/lib/python2.6/site-packages:$PYTHONPATH

    #. In the folder resulting from the :mod:`pyxnat` tarball, run the
       following command::

	python setup.py install --prefix ~/usr

       You should not be required to become administrator, provided you have
       write access to the destination folder.

Installing for all users
........................

If you have administrator rights and want to install for all users, all
you need to do is to go in directory created by expanding the :mod:`pyxnat`
tarball and run the following line::

    python setup.py install

For Unix users, we suggest that you install in '/usr/local' in
order not to interfere with your system::

    python setup.py install --prefix /usr/local
