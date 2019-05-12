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
- `*requests* <https://2.python-requests.org/en/master/>` v2.20
- `*python-lxml* <https://lxml.de/>` v4.3.2+ recommended, earlier versions may work.

For development purposes:

- *python-nose* v1.2.1+ to run the unit tests
- *coverage* v3.6+
- *numpydoc* to build documentation


The `easy_install` way
-----------------------

The easiest way to install :mod:`pyxnat` is (provided that you have `setuptools`
installed) to run::

    easy_install pyxnat

You may need to run the above command as administrator

On a unix environment, it is better to install outside of the hierarchy
managed by the system:

    easy_install --prefix /usr/local pyxnat

.. warning::

    Packages installed via `easy_install` override the Python module look
    up mechanism and thus can confused people not familiar with
    setuptools. Although it may seem harder, we suggest that you use the
    manual way, as described in the following paragraph.

The manual way
---------------

To install :mod:`pyxnat` first download the latest tarball (follow the link on
the bottom of http://pypi.python.org/pypi/pyxnat) and expand it.

Installing in a local environment
..................................

If you don't need to install for all users, we strongly suggest that you
create a local environment and install :mod:`pyxnat` in it. One of the pros of
this method is that you never have to become administrator, and thus all
the changes are local to your account and easy to clean up.

    #. First, create the following directory (where `~` is your home
       directory, or any directory that you want to use as a base for
       your local Python environment, and `X` is your Python version
       number, e.g. `2.6`)::

	~/usr/lib/pythonX/site-packages

    #. Second, make sure that you add this directory in your environment
       variable `PYTHONPATH`. Under window you can do this by editing
       your environment variables in the system parameters dialog. Under
       Unix you can add the following line to your `.bashrc` or any file
       source at login::

	export PYTHONPATH=$HOME/usr/lib/python2.6/site-packages:$PYTHONPATH

    #. In the directory created by expanding the `pyxnat` tarball, run the
       following command::

	python setup.py install --prefix ~/usr

       You should not be required to become administrator, if you have
       write access to the directory you are installing to.

Installing for all users
........................

If you have administrator rights and want to install for all users, all
you need to do is to go in directory created by expanding the `pyxnat`
tarball and run the following line::

    python setup.py install

If you are under Unix, we suggest that you install in '/usr/local' in
order not to interfere with your system::

    python setup.py install --prefix /usr/local


Testing
.......

Go in the directory 'pyxnat/tests' and run the `nosetests` command.
