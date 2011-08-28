from glob import glob

from lxml import etree


class XpathStore(object):

    def __init__(self, interface):
        self._intf = interface
        self._xml = None
        self._nsmap = {}

    def __call__(self, xpath):
        if self._xml is None:
            self._load()

        return self._xml.xpath(xpath, namespaces=self._nsmap)

    def _load(self):
        roots = []
        nsmap = {}

        for xml_file in glob('%s/*.xml' % self._intf._cachedir):
            roots.append(etree.fromstring(open(xml_file, 'rb').read()))
            nsmap.update(roots[-1].nsmap)

        self._xml = etree.Element('Store')
        self._xml.extend(roots)
        self._nsmap = nsmap

    def update(self, new=False):
        pass

