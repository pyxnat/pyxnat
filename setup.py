#!/usr/bin/env python

import setuptools
import os.path as op


def get_version():
    try:
        import re
        import os.path as op
        fp = op.join(op.dirname(__file__), 'pyxnat', 'version.py')
        s = re.search(r'{}\s*=\s*[\'"]([^\'"]*)[\'"]'.format('VERSION'),
                      open(fp).read())
        return s.group(1)
    except Exception:
        raise RuntimeError("No version found")


this_directory = op.abspath(op.dirname(__file__))
with open(op.join(this_directory, 'README.rst')) as f:
    long_description = f.read()


setuptools.setup(name='bbrc-pyxnat',
      version=get_version(),
      summary='XNAT in Python',
      author='Yannick Schwartz',
      author_email='yannick.schwartz@cea.fr',
      url='http://packages.python.org/pyxnat/',
      packages=setuptools.find_packages(exclude=('doc*', 'tests')),
      description='XNAT in Python',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      license='BSD',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Education',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities',
          'Topic :: Internet :: WWW/HTTP',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Programming Language :: Python :: 2.7',
      ],

      platforms='any',
      scripts=['bin/sessionmirror.py'],
      install_requires=['lxml>=4.3',
        'requests>=2.20',
        'requests[security]'],
      package_data={'pyxnat': ['README.rst'], },

      )
