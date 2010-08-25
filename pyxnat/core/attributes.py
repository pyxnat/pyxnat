import difflib

from .jsonutil import JsonTable
from .uriutil import uri_parent

class EAttrs(object):
    def __init__(self, eobj):
        self._eobj = eobj
        self._intf = eobj._intf
        self._datatype = None
        self._id = None

    def __call__(self):
        return self._intf.select(
                    'xnat:subjectData', 
                     self._intf.inspect.datatypes(self._get_datatype())
                        ).where('%s/ID = %s AND'%(self._get_datatype(), 
                                                  self._get_id()))[0]

    def _get_datatype(self):
        if self._datatype is None:
            self._datatype = self._eobj.datatype()

        return self._datatype

    def _get_id(self):
        if self._id is None:
            self._id = self._eobj.id()

        return self._id

    def set(self, path, value):
        value = value.replace(' ', '\s')
        put_uri = self._eobj._uri+'?%s=%s'%(path, value)

        print 'PUT', put_uri
        self._intf._exec(put_uri, 'PUT')

    def mset(self, dict_attrs):
        for path in dict_attrs:
            dict_attrs[path] = dict_attrs[path].replace(' ', '\s')

        query_str = '?'+'&'.join(['%s=%s'%items for items in dict_attrs.items()])
        put_uri = self._eobj._uri + query_str

        print 'PUT', put_uri
        self._intf._exec(self._eobj._uri + query_str, 'PUT')

    def get(self, path):
        query_str = '?columns=ID,%s'%path

        get_uri = uri_parent(self._eobj._uri) + query_str
        jdata = JsonTable(self._intf._get_json(get_uri)).where(ID=self._get_id())

        # unfortunately the return headers do not always have the expected name
        header = difflib.get_close_matches(path, jdata.headers())[0]
        return jdata.get(header).replace('\s', ' ')

    def mget(self, paths):
        query_str = '?columns=ID,'+','.join(paths)

        get_uri = uri_parent(self._eobj._uri) + query_str
        jdata = JsonTable(self._intf._get_json(get_uri)).where(ID=self._get_id())

        results = []

        # unfortunately the return headers do not always have the expected name
        for path in paths:
            header = difflib.get_close_matches(path, jdata.headers())[0]
            results.append(jdata.get(header).replace('\s', ' '))
                
        return results

