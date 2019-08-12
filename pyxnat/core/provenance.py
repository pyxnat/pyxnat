import time
import platform
import socket

from lxml import etree
from lxml.etree import Element, QName

from .uriutil import uri_parent
from .jsonutil import JsonTable
from . import httputil

_nsmap = {'xnat':'http://nrg.wustl.edu/xnat',
          'prov':'http://www.nbirn.net/prov',
          'xsi':'http://www.w3.org/2001/XMLSchema-instance'
          }

_required = ['program', 'timestamp', 'user', 'machine', 'platform']
_optional = ['program_version', 'program_arguments',
             'cvs',
             'platform_version',
             'compiler', 'compiler_version',
             'library', 'library_version'
             ]

_all = ['program', 'program_version', 'program_arguments',
        'timestamp',
        'cvs',
        'user',
        'machine',
        'platform', 'platform_version',
        'compiler', 'compiler_version',
        # 'library', 'library_version'
        ]

_platform_name, _hostname, \
_platform_version, _platform_version2,\
_machine, _machine2 = platform.uname()
_machine = socket.gethostname()


def provenance_document(eobj, process_steps, overwrite):
    root_node = etree.fromstring(eobj.get())

    existing_prov = None
    for child in root_node.getchildren():
        if str(child.tag).endswith('provenance'):
            existing_prov = child
            break

    if existing_prov is not None and not overwrite:
        prov_node = existing_prov
    else:
        if existing_prov is not None and overwrite:
            root_node.remove(existing_prov)

        prov_node = Element(QName(_nsmap['xnat'], 'provenance'),
                            nsmap=_nsmap
                            )
        root_node.insert(0, prov_node)

    prov_node.extend(provenance_parameters(process_steps))

    return etree.tostring(root_node.getroottree())


def provenance_parameters(process_steps):
    prov = []

    for step in process_steps:

        if not set(_required).issubset(step.keys()):
            missing = list(set(_required).difference(step.keys()))

            raise Exception(('Following attributes are '
                             'required to define provenance: %s' % missing
                             )
                            )

        prov.append(process_step_xml(**step))

    return prov

def process_step_xml(**kwargs):

    step_node = Element(QName(_nsmap['prov'], 'processStep'), nsmap=_nsmap)

    program_node = Element(QName(_nsmap['prov'], 'program'), nsmap=_nsmap)
    program_node.text = kwargs['program']

    if 'program_version' in kwargs.keys():
        program_node.set('version', kwargs['program_version'])

    if 'program_arguments' in kwargs.keys():
        program_node.set('arguments', kwargs['program_arguments'])

    step_node.append(program_node)

    timestamp_node = Element(QName(_nsmap['prov'], 'timestamp'),
                             nsmap=_nsmap
                             )
    timestamp_node.text = kwargs['timestamp']

    step_node.append(timestamp_node)

    if 'cvs' in kwargs.keys():
        cvs_node = Element(QName(_nsmap['prov'], 'cvs'), nsmap=_nsmap)
        cvs_node.text = kwargs['cvs']

        step_node.append(cvs_node)

    user_node = Element(QName(_nsmap['prov'], 'user'), nsmap=_nsmap)
    user_node.text = kwargs['user']

    step_node.append(user_node)

    machine_node = Element(QName(_nsmap['prov'], 'machine'), nsmap=_nsmap)
    machine_node.text = kwargs['machine']

    step_node.append(machine_node)

    platform_node = Element(QName(_nsmap['prov'], 'platform'), nsmap=_nsmap)
    platform_node.text = kwargs['platform']

    if 'platform_version' in kwargs.keys():
        platform_node.set('version', kwargs['platform_version'])

    step_node.append(platform_node)

    if 'compiler' in kwargs.keys():
        compiler_node = Element(QName(_nsmap['prov'], 'compiler'),
                                nsmap=_nsmap
                                )
        compiler_node.text = kwargs['compiler']

        if 'compiler_version' in kwargs.keys():
            compiler_node.set('version', kwargs['compiler_version'])

        step_node.append(compiler_node)

    if 'library' in kwargs.keys():
        library_node = Element(QName(_nsmap['prov'], 'library'),
                                nsmap=_nsmap
                                )
        library_node.text = kwargs['library']

        if 'library_version' in kwargs.keys():
            library_node.set('version', kwargs['library_version'])

        step_node.append(library_node)

    return step_node


class Provenance(object):
    """ Class to annotate processed data with provenance information.
        The following parameters are available:

            - program
            - program_version
            - program_arguments
            - timestamp
            - cvs
            - user
            - machine
            - platform
            - platform_version
            - compiler
            - compiler_version

        Examples
        --------
            >>> prov = {'program':'young',
                        'timestamp':'2011-03-01T12:01:01.897987',
                        'user':'angus',
                        'machine':'war',
                        'platform':'linux',
                        }
            >>> element.provenance.set(prov)
            >>> element.provenance.get()
            >>> element.delete()
    """

    def __init__(self, eobject):
        self._intf = eobject._intf
        self._eobject = eobject

    def set(self, process_steps, overwrite=False):
        """ Set provenance information for the data within this element.

            .. note::

                If some required parameters are not provided, theses
                parameters will be extracted from the current machine
                and set automatically. Those parameters are:
                
                    - machine
                    - platform
                    - timestamp
                    - user

            .. warning::
                overwrite option doesn't work because of a bug with the
                allowDataDeletion flag in XNAT

            Parameters
            ----------
            process_steps: list or dict
                dict or list of dicts to define the processing steps
                of the data. The minimum set of information to give
                is: program, timestamp, user, machine and platform. More
                keywords in the class documentation.
            overwrite: boolean
                If False the process_steps are added to the existing ones.
                Else the processing steps overwrite any existing provenance.
        """
        if isinstance(process_steps, dict):
            process_steps = [process_steps]

        for process_step in process_steps:
            _timestamp = time.strftime('%Y-%m-%dT%H:%M:%S',
                                       time.localtime()
                                       )

            if not 'machine' in process_step.keys():
                process_step['machine'] = _machine
            if not 'platform' in process_step.keys():
                process_step['platform'] = _platform_name
                process_step['platform_version'] = _platform_version
            if not 'timestamp' in process_step.keys():
                process_step['timestamp'] = _timestamp
            if not 'user' in process_step.keys():
                process_step['user'] = self._intf._user

        doc = provenance_document(self._eobject, process_steps, overwrite).decode('utf-8')

        body, content_type = httputil.file_message(
            doc, 'text/xml', 'prov.xml', 'prov.xml')

        prov_uri = self._eobject._uri

        if overwrite:
            prov_uri += '?allowDataDeletion=true'

        self._intf._exec(prov_uri,
                         method='PUT',
                         body=body,
                         headers={'content-type':content_type}
                         )

    def get(self):
        """ Gets all the provenance information for that object.

            Returns
            -------
            A list of dicts.
        """
        datatype = self._eobject.datatype()

        columns = ['%s/ID' % datatype] + [
            '%s/provenance/processStep/%s' % (datatype, field)
            for field in _all
            ]

        prov_uri = uri_parent(self._eobject._uri)
        prov_uri += '?columns='
        prov_uri += ','.join(columns)

        steps = []

        table = JsonTable(self._intf._get_json(prov_uri))

        id_header = 'ID' if table.has_header('ID') \
            else '%s/id' % datatype.lower()

        for step in table.where(**{id_header:self._eobject.id()}):
            step_dict = {}
            for key in step.keys():
                if 'processstep' in key:
                    step_dict[key.split('processstep/')[1]] = step[key]

            steps.append(step_dict)

        return steps

    def delete(self):
        """ Removes the provenance attached to this object.

            .. warning::
                doesn't work because of a bug with the allowDataDeletion
                flag in XNAT
        """

        provenance_node = self._eobject.xpath('//xnat:provenance')

        if provenance_node != []:
            provenance_node = provenance_node[0]

            parent_node = provenance_node.getparent()
            parent_node.remove(provenance_node)

            doc = etree.tostring(parent_node.getroottree())

            body, content_type = httputil.file_message(
                doc, 'text/xml', 'prov.xml', 'prov.xml')

            self._intf._exec(
                '%s?allowDataDeletion=true' % self._eobject._uri,
                method='PUT',
                body=body,
                headers={'content-type':content_type}
                )
