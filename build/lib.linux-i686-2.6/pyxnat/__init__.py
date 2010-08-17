""" pyxnat is a simple python library that relies on the REST API provided
by the XNAT platform since its 1.4 version. XNAT is an extensible database for neuroimaging data. The main objective is to ease communications with an XNAT
server to plug-in external tools or python scripts to process the data. It
features:

    #. resources browsing capabilities
    #. read and write access to resources
    #. complex searches
    #. disk-caching of requested files and resources

.. [#] http://www.xnat.org/
.. [#] http://packages.python.org/pyxnat/

____

    **A short overview**    

    *Setup the connection*
        >>> from pyxnat import Interface
        >>> interface = Interface(server='http://central.xnat.org:8080',
                                  user='login',
                                  password='pass',
                                  cachedir=os.path.join(os.path.expanduser('~'),
                                                        '.store')
                                  )

    *Browse the resources*
        >>> interface.select.projects().get()
        [u'CENTRAL_OASIS_CS', u'CENTRAL_OASIS_LONG', ...]

    *Create new resources*
        >>> interface.select.project('my_project').create()
        >>> interface.select.project('my_project').resource('images').file('image.nii').put('/tmp/image.nii')

    *Make complex searches*
        >>> table = interface.select('xnat:subjectData', ['xnat:subjectData/PROJECT', 'xnat:subjectData/SUBJECT_ID']
                            ).where([('xnat:subjectData/SUBJECT_ID','LIKE','%'),
                                     ('xnat:subjectData/PROJECT', '=', 'my_project'),
                                     'AND'
                                     ])

"""

__version__ = '0.6.0'

from .core import Interface, SearchManager, Select, Inspector, Users
from .core import attributes, cache, help, interfaces, jsonutil, resources, \
                  schema, search, select, uriutil, users
