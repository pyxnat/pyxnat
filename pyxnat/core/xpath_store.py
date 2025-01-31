import re
from lxml import etree

from .jsonutil import JsonTable


def get_subject_id(location):
    f = open(location, 'rb')
    content = f.read()
    f.close()

    subject = re.findall(r'<xnat:Subject\sID="(.*?)"\s', content)

    if subject != []:
        return subject[0]


class XpathStore(object):

    """ This utility class is used to query XML files describing XNAT
        subjects but which are stored in the cache directory. Xpath is
        used as the query lanaguage but a few helpers are provided
        to make simple queries.
    """

    def __init__(self, interface):
        self._intf = interface
        self._nsmap = {}
        self._tree = etree.Element('Store')

    def __call__(self, xpath):
        if self._tree is None:
            self._load()

        return self._tree.xpath(xpath, namespaces=self._nsmap)

    def _load(self, content):
        if not content:
            return
        new_subject = etree.fromstring(content)
        self._nsmap = new_subject.nsmap
        subject_id = new_subject.xpath('@ID')[0]
        old_subject = self.subject(subject_id)
        if old_subject:
            self._tree.replace(old_subject, new_subject)
        else:
            self._tree.append(new_subject)

    def _last_modified(self):
        entry_point = self._intf._get_entry_point()
        uri = '%s/subjects?columns=last_modified' % entry_point

        return dict(JsonTable(self._intf._get_json(uri),
                              order_by=['ID', 'last_modified']
                              ).select(['ID', 'last_modified']
                                       ).items())

    def update(self):
        """ Updates the xml files in the cachedir.
        """

        self.checkout(subjects=self.subjects())

    def checkout(self, project=None, subjects=None):
        """ Downloads all the subject XMLs for a project or a list
            of subjects.

            Parameters
            ----------
            project: str
                The id of the project
            subjects: list
                List of subjects that have to be downloaded.
        """
        if project is not None and subjects is None:
            for s in self._intf.select('/project/%s/subjects' % project):
                self._load(s.get())
        elif subjects is not None:
            for sid in subjects:
                self._load(self._intf._exec('%s/subjects/%s?format=xml' % (
                          self._intf._get_entry_point(), sid))
                          )

    def subject(self, subject_id):
        tmp = self.__call__('//xnat:Subject[@ID="%s"]' % (subject_id))

        if len(tmp) > 0:
            return tmp[1]
        return None

    def subjects(self):
        """ Returns all the subject ids.
        """
        return self.__call__('//xnat:Subject/attribute::ID')

    def keys(self):
        """ Returns attribute keys at the subject level.
        """
        return self.element_keys('xnat:Subject')

    def values(self, key):
        """ Returns the values for all subjects for a specific attribute.
        """
        return self.element_values('xnat:Subject', key)

    def attrs(self):
        """ Returns the attributes of all subjects.
        """
        return self.element_attrs('xnat:Subject')

    def elements(self):
        """ Returns the element names for all subjects elements.

            .. note:: in xpath terms, this function is returning all
                the names of the subjects descendant nodes.
        """
        elements = set()

        for element in self.__call__('//xnat:Subject/descendant::*'):
            for ns in element.nsmap:
                if element.nsmap[ns] in element.tag:
                    n = element.tag.replace('{%s}' % element.nsmap[ns],
                                            '%s:' % ns)
                    elements.add(n)

        return list(elements)

    def element_attrs(self, name):
        """ Returns the attributes of this specific element.
        """
        attrs = []

        for element in self.__call__('//%s' % name):
            attrs.append(element.attrib)

        return attrs

    def element_keys(self, name):
        """ Returns the attribute keys of this specific element.
        """
        keys = set()

        for element in self.__call__('//%s' % name):
            for element_key in element.keys():
                keys.add(element_key)

        return list(keys)

    def element_values(self, name, key):
        """ Returns the attribute values of this specific element.
        """
        values = set()

        for subject in self.__call__('//%s' % name):
            values.add(subject.get(key))

        return list(values)

    def element_text(self, name):
        """ Returns the text values of this specific element.
        """
        return list(set(self.__call__('//%s/child::text()' % name)))
