import os
import tempfile

from .jsonutil import JsonTable, csv_to_json
from .resources import CObject


class Tags(object):
    """ Database tags sub-interface.
        It is meant to be an attribute of the main Interface class.
    """

    def __init__(self, interface):
        self._intf = interface
        self._meta_project = None

    def __call__(self):
        self._init()
        return self._meta_project.subject(self._intf._user
                                          ).resource('tags').files().get()

    def _init(self):
        if self._meta_project is None:
            self._meta_project = \
                self._intf.select.project('metabase_%s' % self._intf._user)
            if self._meta_project.accessibility() != 'private':
                self._meta_project.set_accessibility('private')

        if not self._meta_project.exists():
            self._meta_project.create()
            self._meta_project.set_accessibility('private')

    def new(self, name):
        return self.get(name).create()

    def delete(self, name):
        self.get(name).delete()

    def get(self, name):
        return Tag(name, self._intf)

    def share(self, other_user):
        if self._intf.select.project('metabase_%s' % other_user).exists():
            self._meta_project.subject(self._intf._user
                                       ).share('metabase_%s' % other_user)


class Tag(object):
    def __init__(self, name, interface):
        self._name = name
        self._intf = interface
        self._intf.manage.tags._init()
        self._file = self._intf.manage.tags._meta_project.subject(
            self._intf._user).resource('tags').file(name)

    def __repr__(self):
        return '<Tag> %s' % self._name

    def _read(self):
        fd = open(self._file.get(), 'rb')
        jtag = JsonTable(csv_to_json(fd.read()))
        fd.close()

        return jtag

    def create(self):
        if not self.exists():
            jtag = JsonTable([])
            tmp = tempfile.mkstemp()[1]
            jtag.dump_csv(tmp)
            self._file.put(tmp)
            os.remove(tmp)

        return self

    def delete(self):
        if self.exists():
            self._file.delete()

    def exists(self):
        return self._file.exists()

    def dereference(self, uri):
        jtag = self._read()
        tmp = tempfile.mkstemp()[1]
        jtag.where_not(URI=uri).dump_csv(tmp)
        self._file.put(tmp)
        os.remove(tmp)

    def dereference_many(self, uris=[]):
        jtag = self._read()
        for uri in uris:
            jtag = jtag.where_not(URI=uri)
        tmp = tempfile.mkstemp()[1]
        jtag.dump_csv(tmp)
        self._file.put(tmp)
        os.remove(tmp)

    def reference(self, uri):
        uri = self._intf.select(uri)._uri
        jtag = self._read()
        if uri not in jtag.get('URI', always_list=True):
            jtag.data.append({'URI': uri})
            tmp = tempfile.mkstemp()[1]
            jtag.dump_csv(tmp)
            self._file.put(tmp)
            os.remove(tmp)

    def reference_many(self, uris=[]):
        jtag = self._read()
        for uri in uris:
            jtag.data.append({'URI': uri})
        tmp = tempfile.mkstemp()[1]
        jtag.dump_csv(tmp)
        self._file.put(tmp)
        os.remove(tmp)

    def references(self, show_uris=False):
        jtag = self._read()
        uris = jtag.get('URI', always_list=True)

        if not show_uris:
            return CObject(uris, self._intf)
        return uris
