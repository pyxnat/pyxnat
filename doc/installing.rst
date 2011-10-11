Installing pyxnat
===================


Platforms
---------

OS Independent.

It was tested under:
    - Ubuntu 10.04 with python 2.6
    - Ubuntu 11.04 with python 2.7
    - Debian Squeeze with python 2.6
    - Windows XP with python 2.7
    - Mac OS X untested but should work with python >= 2.6

Prerequisites
-------------

- *python* v2.6+

- *python-lxml* v1.3.6+ recommanded, earlier versions may work:
  Lxml may be installed using standard Python distribution tools, here are the 
  recommanded ones. For more details on installing procedures please see the 
  sections following this one.

        #. easy_install: lxml may be installed via easy_install under 
           Unix and Windows

        #. Windows only: installers are provided 
	   `here <http://pypi.python.org/pypi/lxml/2.2.8>`_, select the .exe for
	   your python version and install.

	#. Most linux distributions provide a package for lxml. e.g. for debian
	   or debian-based distributions:

	   .. code-block:: none
	   
	      apt-get install python-lxml

        #. Mac OS X: a macport of lxml is available, see lxml site for further information. 
                     Alternatively, you can compile the package from sources by following 
                     the instructions. If the recommanded command on the site fails:

		     .. code-block:: none

                        python setup.py build --static-deps

                     Try forcing an older version of libxml2:

		     .. code-block:: none

                        python setup.py build --static-deps --libxml2-version=2.7.3

                     Do not forget to add lxml to your PYTHONPATH afterwards.

- python-httplib2 v0.6+, a version above 0.7 is however recommanded:

  #. On all platforms:

     .. code-block:: none

		     easy_install httplib2

  #. Or with the packaging system on linux e.g. for debian:

     .. code-block:: none

		     apt-get install python-httplib2

- *python-nose* v0.10+ to run the unit tests

- *networkx* and *matplotlib* are not mandatory:
    These libraries are used to make some graphical representations.

The `easy_install` way
-----------------------

The easiest way to install pyxnat is (provided that you have `setuptools`
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

To install pyxnat first download the latest tarball (follow the link on
the bottom of http://pypi.python.org/pypi/pyxnat) and expand it.

Installing in a local environment
..................................

If you don't need to install for all users, we strongly suggest that you
create a local environment and install `pyxnat` in it. One of the pros of
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


