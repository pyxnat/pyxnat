from six import string_types
# REST collection resources tree
resources_tree = {
    'projects': ['subjects', 'resources'],
    'subjects': ['experiments', 'resources'],
    'experiments': ['assessors', 'reconstructions', 'scans', 'resources'],
    'assessors': ['resources', 'in_resources', 'out_resources'],
    'reconstructions': ['in_resources', 'out_resources'],
    'scans': ['resources'],
    'resources': ['files'],
    'files': [],
    'in_resources': ['files'],
    'in_files': [],
    'out_resources': ['files'],
    'out_files': [],
    }

prearc_tree = {'projects': ['scans'],
               'scans': ['resources'],
               'resources': ['files']
               }
# REST resources that are not natively supported
extra_resources_tree = {'projects': ['assessors', 'scans', 'reconstructions'],
                        'subjects': ['assessors', 'scans', 'reconstructions'],
                        }

# REST <Python to URI> translation table
rest_translation = {'in_resources': 'in/resources',
                    'in_files': 'in/files',
                    'out_resources': 'out/resources',
                    'out_files': 'out/files',
                    'in_resource': 'in/resource',
                    'in_file': 'in/file',
                    'out_resource': 'out/resource',
                    'out_file': 'out/file',
                    }


# REST json format <id_header, label_header>
json = {'projects': ['ID', 'ID'],
        'subjects': ['ID', 'label'],
        'experiments': ['ID', 'label'],
        'assessors': ['ID', 'label'],
        'reconstructions': ['ID', 'label'],
        'scans': ['ID', 'ID'],
        'resources': ['xnat_abstractresource_id', 'label'],
        'out_resources': ['xnat_abstractresource_id', 'label'],
        'in_resources': ['xnat_abstractresource_id', 'label'],
        'files': ['path', 'path']}

resources_singular = [key.rsplit('s', 1)[0] for key in resources_tree.keys()]
resources_plural = resources_tree.keys()
resources_types = resources_singular + list(resources_plural)

default_datatypes = {'projects': 'xnat:projectData',
                     'subjects': 'xnat:subjectData',
                     'experiments': 'xnat:mrSessionData',
                     'assessors': 'xnat:mrAssessorData',
                     'reconstructions': 'xnat:reconstructedImageData',
                     'scans': 'xnat:mrScanData',
                     'resources': None,
                     'in_resources': None,
                     'out_resources': None,
                     }


def datatype_attributes(root, datatype):
    def _iterchildren(node, pathsofar):
        elements = []

        for child in node.iterchildren():
            if isinstance(child.tag, string_types) \
               and child.tag.split('}')[1] == 'element':
                elements.append('%s/%s' % (pathsofar, child.get('name')))
                elements.extend(_iterchildren(child, '%s/%s' %
                                (pathsofar, child.get('name'))))

            elif isinstance(child.tag, string_types) and \
                    child.tag.split('}')[1] == 'attribute':
                elements.append('%s/%s' % (pathsofar, child.get('name')))

            elif isinstance(child.tag, string_types) \
                    and child.tag.split('}')[1] == 'extension':

                ct_xpath = "/xs:schema/xs:complexType[@name='%s']" % \
                    child.get('base').split(':')[1]

                rt = node.getroottree()
                for complex_type in rt.xpath(ct_xpath, namespaces=child.nsmap):

                    same = False

                    for ancestor in child.iterancestors():
                        if ancestor.get('name') == \
                                child.get('base').split(':')[1]:
                            same = True
                            break

                    if not same:
                        elements.extend(_iterchildren(complex_type,
                                                      pathsofar)
                                        )

                    elements.extend(_iterchildren(child, pathsofar))

            else:
                elements.extend(_iterchildren(child, pathsofar))

        return elements

    ct_xpath = "/xs:schema/xs:complexType[@name='%s']" % \
        datatype.split(':')[1]

    attributes = []

    for complex_type in root.xpath(ct_xpath, namespaces=root.nsmap):
        for child in complex_type.iterchildren():
            attributes.extend(_iterchildren(child, datatype))

    return attributes


def datatypes(root):
    nsmap = get_nsmap(root)

    return [element.get('type')
            for element in root.xpath('/xs:schema/xs:element',
                                      namespaces=nsmap)]
                                      

def get_nsmap(node):
    nsmap = node.nsmap
    none_ns = node.nsmap.get(None)

    if none_ns is None:
        nsmap[none_ns.rsplit('/', 1)[1]] = none_ns
        del nsmap[None]

    return nsmap


def class_name(self):
    """
    Return the name of this class without qualification.
    eg. If the class name is "x.y.class" return only "class"
    """
    return self.__class__.__name__.split('.')[-1]
