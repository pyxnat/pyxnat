#!/usr/bin/env python

from distutils.core import setup
import sys,os

# For some commands, use setuptools
if len(set(['develop', 'sdist', 'release', 'bdist_egg', 'bdist_rpm', 'bdist',
            'bdist_dumb', 'bdist_wininst', 'install_egg_info', 'build_sphinx',
            'egg_info', 'easy_install', 'upload']).intersection(sys.argv)) > 0:
    from setupegg import extra_setuptools_args

# extra_setuptools_args is injected by the setupegg.py script, for
# running the setup with setuptools.
if not 'extra_setuptools_args' in globals():
    extra_setuptools_args = dict()

def get_version():
    basedir = os.path.dirname(__file__)
    with open(os.path.join(basedir, 'pyxnat/version.py')) as f:
        VERSION = None
        exec(f.read())
        return VERSION
    raise RuntimeError("No version found")

LONG_DESCRIPTION = """
The package is hosted at VUIIS github repo, which is a customized PyXnat with cache feature (debugging, testing purpose)
The main purpose is to explicitly display all incoming URL queries and open session IDs.

PyXNAT
======

pyxnat provides an API to access data on XNAT (see http://xnat.org)
servers.

Visit http://packages.python.org/pyxnat for more information.
"""

setup(name='pyxnat_ldax',
      version=get_version(),
      summary='XNAT in Python for LDax',
      author='Shunxing Bao',
      author_email='onealbao@gmail.com',
      url='https://github.com/VUIIS/pyxnat',
      packages=['pyxnat'],
      package_data={'pyxnat': ['externals/*.py',
                               'externals/httplib2/*.py',
                               'externals/simplejson/*.py',
                               'tests/*.py',
                               'tests/*.txt',
                               'tests/*.csv',
                               'core/*.py',
                               '*.py'],
                    },
      description="""Xnat in Python""",
      long_description=LONG_DESCRIPTION,
      license='BSD',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
      ],

      platforms='any', 
      requires=['requests'],
      install_requires=['requests', 'lxml', 'requests[security]'],
      **extra_setuptools_args)
