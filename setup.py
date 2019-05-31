#!/usr/bin/env python

from distutils.core import setup
import sys, os

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
    try:
        import re
        import os.path as op
        fp = op.join(op.dirname(__file__), 'pyxnat', 'version.py')
        s = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format('VERSION'),
            open(fp).read())
        return s.group(1)
    except:
        raise RuntimeError("No version found")

LONG_DESCRIPTION = """
PyXNAT
======

pyxnat provides an API to access data on XNAT (see http://xnat.org)
servers.

Visit https://pyxnat.readthedocs.io/en/latest/ for more information.
"""

setup(name='pyxnat',
      version=get_version(),
      summary='XNAT in Python',
      author='Yannick Schwartz',
      author_email='yannick.schwartz@cea.fr',
      url='http://packages.python.org/pyxnat/',
      packages=['pyxnat'],
      package_data={'pyxnat': ['core/*.py', '*.py'], },
      description="""XNAT in Python""",
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
      install_requires=['lxml>=4.3', 'requests>=2.20', 'requests[security]'],
      **extra_setuptools_args)
