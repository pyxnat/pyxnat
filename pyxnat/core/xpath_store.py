from os import path
from glob import iglob

from lxml import etree


class XpathStore(object):

    def __init__(self, interface):
        self._intf = interface
        self._tree = None
        self._nsmap = {}

    def __call__(self, xpath):
        if self._tree is None:
            self._load()

        return self._tree.xpath(xpath, namespaces=self._nsmap)

    def _load(self):
        roots = []
        nsmap = {}

        for doc in iglob('%s/*.xml' % self._intf._cachedir):
            roots.append(etree.fromstring(open(doc, 'rb').read()))
            nsmap.update(roots[-1].nsmap)

        self._tree = etree.Element('Store')
        self._tree.extend(roots)
        self._nsmap = nsmap

    def _last_modified(self):
        entry_point = self._intf._get_entry_point()
        uri = '%s/subjects?columns=last_modified' % entry_point

        return dict(JsonTable(self._intf._get_json(uri), 
                              order_by=['ID', 'last_modified']
                              ).select(['ID', 'last_modified']
                                       ).items()
                    )

    def update(self, all_types=False):
        """ Updates the xml files in the cachedir.

            Parameters
            ----------
            all_type: boolean
                If all_types is True, all the xml files will be updated
                and downloaded if necessary. Checking of the local version
                is up to date is only possible for subject XMLs.
                If all_types is False, only the subject XMLs will be updated.
        """

        last_modified = self._last_modified()
        
        for doc in iglob('%s/*.xml' % self._intf._cachedir):
            if is_subject(doc):
                path.getmtime(doc)


        # datetime.datetime.strptime(, '%Y-%m-%d %H:%M:%S')


