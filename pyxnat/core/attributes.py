import difflib
import urllib

from .jsonutil import JsonTable
from .uriutil import uri_parent
from .schema import datatype_attributes


class EAttrs(object):
    """ Accessor class to resource fields.

        Help to retrieve the attributes paths relevant to this element::
            >>> subject.attrs()
            ['xnat:subjectData/sharing',
             'xnat:subjectData/sharing/share',
             'xnat:subjectData/resources',
             ...
             'xnat:subjectData/experiments/experiment'
             ]

         All paths are not valid but they give an indication of what
         is available. To retrieve the paths, the corresponding
         schemas must be downloaded first through the schema
         management interface in order to be parsed::
             >>> interface.manage.schemas.add('xnat.xsd')
             >>> interface.manage.schemas.add('myschema/myschema.xsd')
    """
    def __init__(self, eobj):
        """
            Parameters
            ----------
            eobj:
                :class:`EObject` Object
        """
        self._eobj = eobj
        self._intf = eobj._intf
        self._datatype = None
        self._id = None

    def __call__(self):
        """ List the attributes paths relevant to this element.
        """
        paths = []
        self._intf.manage.schemas._init()
        for root in self._intf.manage.schemas._trees.values():
            paths.extend(datatype_attributes(root, self._get_datatype()))
        return paths

    def _get_datatype(self):
        if self._datatype is None:
            self._datatype = self._eobj.datatype()

        return self._datatype

    def _get_id(self):
        if self._id is None:
            self._id = self._eobj.id()

        return self._id

    def set(self, path, value, **kwargs):
        """ Set an attribute.

            Parameters
            ----------
            path: string
                The xpath of the attribute relative to the element.
            value: string
                The attribute's value. Note that the python type is
                always a string but the content of the value must
                match what is defined in the schema.
                    e.g. an element defined as a float in the schema
                    must be given a string containing a number, a
                    valid date must follow the ISO 8601 which is the
                    standard representation for dates and times
                    established by the W3C.
        """
        put_uri = self._eobj._uri + '?xsiType=%s&%s=%s' % (urllib.quote(self._get_datatype())
                                                         , urllib.quote(path)
                                                         , urllib.quote(value)
                                              )

        self._intf._exec(put_uri, 'PUT', **kwargs)

    def mset(self, dict_attrs, **kwargs):
        """ Set multiple attributes at once.

            It is more efficient to use this method instead of
            multiple times the `set()` method when setting more than
            one attribute because only a single HTTP call is issued to
            the server.

            Parameters
            ----------
            dict_attrs: dict
                The dict of key values to set. It follows the same
                principles as the single `set()` method.
        """

        query_str = '?xsiType=%s' % (urllib.quote(self._get_datatype())) + ''.join(['&%s=%s' % (urllib.quote(path),
                                               urllib.quote(val)
                                               )
                                    for path, val in dict_attrs.items()
                                    ]
                                   )

        put_uri = self._eobj._uri + query_str

        self._intf._exec(put_uri, 'PUT', **kwargs)

    def get(self, path):
        """ Get an attribute value.

            .. note::
                The value is always returned in a Python string. It must
                be explicitly casted or transformed if needed.

            Parameters
            ----------
            path: string
                The xpath of the attribute relative to the element.

            Returns
            -------
            A string containing the value.
        """
        query_str = '?columns=ID,%s' % path

        get_uri = uri_parent(self._eobj._uri) + query_str
        jdata = JsonTable(self._intf._get_json(get_uri)
                          ).where(ID=self._get_id())

        # unfortunately the return headers do not always have the
        # expected name

        header = difflib.get_close_matches(path.split('/')[-1],
                                           jdata.headers()
                                           )
        if header == []:
            header = difflib.get_close_matches(path, jdata.headers())[0]
        else:
            header = header[0]

        replaceSlashS = lambda x : x.replace('\s', ' ')
        if type(jdata.get(header)) == list:
            return map(replaceSlashS, jdata.get(header))
        else:
            return jdata.get(header).replace('\s', ' ')

    def mget(self, paths):
        """ Set multiple attributes at once.

            It is more efficient to use this method instead of
            multiple times the `get()` method when getting more than
            one attribute because only a single HTTP call is issued to
            the server.

            Parameters
            ----------
            paths: list
                List of attributes' paths.

            Returns
            -------
            list: ordered list of values (in the order of the
            requested paths)
        """

        query_str = '?columns=ID,%s' % ','.join(paths)
        get_uri = uri_parent(self._eobj._uri) + query_str

        jdata = JsonTable(self._intf._get_json(get_uri)
                          ).where(ID=self._get_id())

        results = []

        # unfortunately the return headers do not always have the
        # expected name

        for path in paths:
            header = difflib.get_close_matches(path.split('/')[-1],
                                               jdata.headers())

            if header == []:
                header = difflib.get_close_matches(path, jdata.headers())[0]
            else:
                header = header[0]
            results.append(jdata.get(header).replace('\s', ' '))

        return results
