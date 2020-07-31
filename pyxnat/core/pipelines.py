import os
import json

# import six
# if six.PY2:
#     from urllib2 import urlopen
# elif six.PY3:
#     from urllib.request import urlopen

# import smtplib
# from copy import deepcopy
# import email.mime.text
# import xml.dom.minidom

# import suds.client
# import suds.xsd.doctor

from . import httputil


class PipelineNotFoundError(Exception):
    """workflow not found"""


class Pipelines(object):

    def __init__(self, project, interface):
        self._intf = interface
        self._project = project

    def get(self):
        response = self._intf._exec('%s/projects/%s/pipelines' % (
                self._intf._get_entry_point(),
                self._project,
                ))

        return json.loads(response)['ResultSet']['Result']

    def add(self, location):
        f = open(location, 'rb')
        pip_doc = f.read()
        f.close()

        body, content_type = httputil.file_message(
            pip_doc, 'text/xml', location, os.path.split(location)[1])

        pipeline_uri = '%s/projects/%s/pipelines/%s' % (
            self._intf._get_entry_point(),
            self._project,
            os.path.split(location)[1]
            )

        self._intf._exec(pipeline_uri,
                         method='PUT',
                         body=body,
                         headers={'content-type': content_type}
                         )

    def delete(self, pipeline_id):
        pass


class Pipeline(object):

    def __init__(self, pipeline_id, interface):
        self._intf = interface
        self._id = pipeline_id

    def run(self):
        pass

    def stop(self):
        pass

    def update(self):
        pass

    def complete(self):
        pass

    def fail(self):
        pass

# class Pipeline(object):

#     """class for mirroring workflow information (XML) in XNAT"""

#     def __init__(self, base_url, username, password, workflow_id):
#         self._base_url = base_url
#         self._username = username
#         self._password = password
#         self._cookiejar = None
#         res = self._call('CreateServiceSession.jws',
#                          'execute',
#                          (),
#                          authenticated=True)
#         self._session = str(res)
#         args = (('ns1:string', self._session),
#                 ('ns1:string', 'wrk:workflowData.ID'),
#                 ('ns1:string', '='),
#                 ('ns1:string', workflow_id),
#                 ('ns1:string', 'wrk:workflowData'))
#         workflow_ids = self._call('GetIdentifiers.jws', 'search', args)
#         self._doc = None
#         for w_id in workflow_ids:
#             url = '%s/app/template/XMLSearch.vm/id/%s/data_type/wrk:workflowData' % (self._base_url, str(w_id))
#             r = urllib2.Request(url)
#             self._cookiejar.add_cookie_header(r)
#             data = urllib2.urlopen(r).read()
#             doc = xml.dom.minidom.parseString(data)
#             workflow_node = doc.getElementsByTagName('wrk:Workflow')[0]
#             status = workflow_node.getAttribute('status').lower()
#             if status in ('queued', 'awaiting action', 'hold'):
#                 self._doc = doc
#                 break
#         if self._doc is None:
#             raise PipelineNotFoundError
#         return

#     def _call(self,
#               jws,
#               operation,
#               inputs,
#               authenticated=False,
#               fix_import=False):
#         """perform a SOAP call"""
#         url = '%s/axis/%s' % (self._base_url, jws)
#         if authenticated:
#             t = suds.transport.http.HttpAuthenticated(username=self._username,
#                                                       password=self._password)
#         else:
#             t = suds.transport.http.HttpTransport()
#         if self._cookiejar is not None:
#             t.cookiejar = self._cookiejar
#         if fix_import:
#             xsd_url = 'http://schemas.xmlsoap.org/soap/encoding/'
#             imp = suds.xsd.doctor.Import(xsd_url)
#             doctor = suds.xsd.doctor.ImportDoctor(imp)
#             client = suds.client.Client('%s?wsdl' % url,
#                                         transport=t,
#                                         doctor=doctor)
#         else:
#             client = suds.client.Client('%s?wsdl' % url, transport=t)
#         typed_inputs = []
#         for (dtype, val) in inputs:
#             ti = client.factory.create(dtype)
#             ti.value = val
#             typed_inputs.append(ti)
#         # the WSDL returns the local IP address in the URLs; these need
#         # to be corrected if XNAT is behind a proxy
#         client.set_options(location=url)
#         f = getattr(client.service, operation)
#         result = f(*typed_inputs)
#         if self._cookiejar is None:
#             self._cookiejar = t.cookiejar
#         return result


#     def _close(self):
#         """close the XNAT session (log out)"""
#         self._call('CloseServiceSession.jws', 'execute', ())
#         return

#     def _update_xnat(self):
#         """update XNAT with the current state of this (WorkflowInfo) object"""
#         inputs = (('ns0:string', self._session),
#                   ('ns0:string', self._doc.toxml()),
#                   ('ns0:boolean', False),
#                   ('ns0:boolean', True))
#         self._call('StoreXML.jws',
#                    'store',
#                    inputs,
#                    authenticated=True,
#                    fix_import=True)
#         return

#     def _append_node(self, root, name, value):
#         """add a simple text node with tag "name" and data "value" under
#         the node "root"
#         """
#         node = self._doc.createElement(name)
#         node.appendChild(self._doc.createTextNode(value))
#         root.appendChild(node)
#         return

#     def set_environment(self, arguments, parameters):
#         """set the execution environment

#         should be run only once before update() is called
#         """
#         # order is important
#         workflow_node = self._doc.getElementsByTagName('wrk:Workflow')[0]
#         ee_node = self._doc.createElement('wrk:executionEnvironment')
#         ee_node.setAttribute('xsi:type', 'wrk:xnatExecutionEnvironment')
#         workflow_node.appendChild(ee_node)
#         self._append_node(ee_node, 'wrk:pipeline', arguments['pipeline'])
#         self._append_node(ee_node, 'wrk:xnatuser', arguments['u'])
#         self._append_node(ee_node, 'wrk:host', arguments['host'])
#         params_node = self._doc.createElement('wrk:parameters')
#         ee_node.appendChild(params_node)
#         for key in parameters:
#             param_node = self._doc.createElement('wrk:parameter')
#             param_node.setAttribute('name', key)
#             for val in parameters[key]:
#                 param_node.appendChild(self._doc.createTextNode(val))
#             params_node.appendChild(param_node)
#         for email in arguments['notify_emails']:
#             self._append_node(ee_node, 'wrk:notify', email)
#         self._append_node(ee_node, 'wrk:dataType', arguments['dataType'])
#         self._append_node(ee_node, 'wrk:id', arguments['id'])
#         if arguments['notify_flag']:
#             self._append_node(ee_node, 'wrk:supressNotification', '0')
#         else:
#             self._append_node(ee_node, 'wrk:supressNotification', '1')
#         return

#     def update(self, step_id, step_description, percent_complete):
#         """update the workflow in XNAT"""
#         workflow_node = self._doc.getElementsByTagName('wrk:Workflow')[0]
#         workflow_node.setAttribute('status', 'Running')
#         t = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
#         workflow_node.setAttribute('current_step_launch_time', t)
#         workflow_node.setAttribute('current_step_id', step_id)
#         workflow_node.setAttribute('step_description', step_description)
#         workflow_node.setAttribute('percentageComplete', percent_complete)
#         self._update_xnat()
#         return

#     def complete(self):
#         """mark the workflow comleted in XNAT and close the session"""
#         workflow_node = self._doc.getElementsByTagName('wrk:Workflow')[0]
#         workflow_node.setAttribute('status', 'Complete')
#         t = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
#         workflow_node.setAttribute('current_step_launch_time', t)
#         workflow_node.setAttribute('percentageComplete', '100.0')
#         try:
#             workflow_node.removeAttribute('current_step_id')
#         except xml.dom.NotFoundErr:
#             pass
#         try:
#             workflow_node.removeAttribute('step_description')
#         except xml.dom.NotFoundErr:
#             pass
#         self._update_xnat()
#         self._close()
#         return

#     def fail(self, description=None):
#         """mark the workflow failed in XNAT and close the session"""
#         workflow_node = self._doc.getElementsByTagName('wrk:Workflow')[0]
#         workflow_node.setAttribute('status', 'Failed')
#         if description is not None:
#             workflow_node.setAttribute('step_description', description)
#         self._update_xnat()
#         self._close()
#         return
