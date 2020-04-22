import urllib

from lxml import etree

from .search import SearchManager
from .users import Users
from .resources import Project
from .tags import Tags
from .jsonutil import JsonTable


class GlobalManager(object):
    """ Mainly a container class to provide a clean interface for all
        management classes.
    """

    def __init__(self, interface):
        self._intf = interface

        self.search = SearchManager(self._intf)
        self.users = Users(self._intf)
        self.tags = Tags(self._intf)
        self.schemas = SchemaManager(self._intf)
        self.prearchive = PreArchive(self._intf)

    def register_callback(self, func):
        """ Defines a callback to execute when collections of resources are
            accessed.

            Parameters
            ----------
            func: callable
                A callable that takes the current collection object as first
                argument and the current element object as second argument.

            Examples
            --------
            >>> def notify(cobj, eobj):
            >>>    print eobj._uri
            >>> interface.manage.register_callback(notify)
        """
        self._intf._callback = func

    def unregister_callback(self):
        """ Unregisters the callback.
        """
        self._intf._callback = None

    def project(self, project_id):
        """ Returns a project manager.
        """
        return ProjectManager(project_id, self._intf)


class ProjectManager(object):
    """ Management interface for projects.

        This functionalities are also available through `Project` objects.
    """

    def __init__(self, project_id, interface):

        self._intf = interface
        self._intf._get_entry_point()

        project = Project('%s/projects/%s' % (self._intf._entry,
                                              project_id
                                              ),
                          self._intf
                          )

        self.prearchive_code = project.prearchive_code
        self.set_prearchive_code = project.set_prearchive_code
        self.quarantine_code = project.quarantine_code
        self.set_quarantine_code = project.set_quarantine_code
        self.current_arc = project.current_arc
        self.set_subfolder_in_current_arc = \
            project.set_subfolder_in_current_arc
        self.accessibility = project.accessibility
        self.users = project.users
        self.owners = project.owners
        self.members = project.members
        self.collaborators = project.collaborators
        self.user_role = project.user_role
        self.add_user = project.add_user
        self.remove_user = project.remove_user


class SchemaManager(object):
    """ Management interface for XNAT schemas.

        The aim is to provide a minimal set of functionalities to parse
        and look at XNAT schemas.
    """

    def __init__(self, interface):
        self._intf = interface
        self._trees = {}

    def __call__(self):
        return self._trees.keys()

    def add(self, url):
        """ Loads an additional schema.

            Parameters
            ----------
            url: str
                url of the schema relative to the server.
                    e.g. for
                    http://central.xnat.org/xapi/schemas/xnat give
                    ``/xapi/schemas/xnat``

        """

        #if not re.match('/?schemas/.*/.*\.xsd', url):
        #    if not 'schemas' in url and re.match('/?\w+/\w+[.]xsd', url):
        #        url = join_uri('/schemas', url)
        #
        #    elif not re.match('^[^/].xsd', url):
        #        url = '/schemas/%s/%s'%(url.split('.xsd')[0], url)
        #    else:
        #        raise NotImplementedError

        self._trees[url.split('/')[-1]] = \
            etree.fromstring(self._intf._exec(url))

    def remove(self, name):
        """ Removes a schema.
        """
        if name in self._trees.keys():
            del self._trees[name]

"""
   Fields Of the Prearchive
   ------------------------
   Each session in the prearchive
    has the following fields:
       "project" - The name of the project. "Unassigned" if the session is unassigned.
       "timestamp" - The time (down to millisecond) that this session was received
                     by XNAT. "20110603_124835868" for example.
       "lastmod" - The time this session as last modified. Moving, resetting etc.
                   updates this time
       "uploaded" - The time this session was uploaded to XNAT. Usually the same as
                    "timestamp"
       "scan_date" - The date this session was scanned.
       "scan_time" - The time this session was scanned.
       "subject" - The name of the subject
       "folderName" - The id of this session. Corresponds to XNAT's session id,
       "name" - The name of this session. Corresponds to XNAT's session label.
       "tag" - This session's unique DICOM identifier. Usually the SOP instance UID.
       "status" - The current status of this session
       "url" - The unique uri of this session.
       "autoarchive" - Whether this session should be auto-archived.
    For more in-depth information about the prearchive see:
    http://docs.xnat.org/Using+the+Prearchive#XNAT%201.5:%20Managing%20Data%20with%20the%20Prearchive-Operations-Session%20Status

    Uniquely identifying a session
    ------------------------------
    Every session in the prearchive uniquely is identified by "project",
    "timestamp" and "folderName".
    (13/7/2011) - Each session could have been uniquely identified by the "url"
                  field or the "tag" field. These are arguably more elegant
                  identifiers but for now the "project", "timestamp", "folderName"
                  triple is used.

"""
class PreArchive(object):
    def __init__(self, interface):
        self._intf = interface

    """
    Retrieve the status of a session
    Parameters
    ----------
       triple - A list containing the project, timestamp and session id, in that order.
    """
    def status(self, triple):
        return JsonTable(
            self._intf._get_json('/data/prearchive/projects')
            ).where(
            project=triple[0], timestamp=triple[1], folderName=triple[2]
            ).get('status')

    """
    Retrieve the contents of the prearchive.
    """
    def get(self):
        return JsonTable(self._intf._get_json('/data/prearchive/projects'),
                         ['project', 'timestamp', 'folderName']
                         ).select(['project', 'timestamp', 'folderName']
                                  ).as_list()[1:]

    """
    Retrieve the scans of a give session triple
    Parameters
    ----------
       triple - A list containing the project, timestamp and session id, in that order.
    """
    def get_scans(self, triple):
        return JsonTable(self._intf._get_json(
                '/data/prearchive/projects/%s/scans' \
                    % '/'.join(triple)
                )).get('ID')

    """
    Retrieve the resource of a session triple
    Parameters
    ----------
       triple - A list containing the project, timestamp and session id, in that order.
       scan_id - id of the scan
    """
    def get_resources(self, triple, scan_id):
        return JsonTable(self._intf._get_json(
                '/data/prearchive/projects/%s'
                '/scans/%s/resources' % ('/'.join(triple), scan_id)
                )).get('label')

    """
    Retrieve a list of files in a given session triple
    Parameters
    ----------
       triple - A list containing the project, timestamp and session id, in that order.
       scan_id - id of the scan
       resource_id - id of the resource
    """
    def get_files(self, triple, scan_id, resource_id):
        return JsonTable(self._intf._get_json(
                '/data/prearchive/projects/%s'
                '/scans/%s/resources/%s/files' % ('/'.join(triple),
                                                  scan_id,
                                                  resource_id)
                )).get('Name')

    """
    Move multiple sessions to a project in the prearchive asynchronously.
    If only one session is it is done now.

    This does *not* archive a session.

    Parameters
    ----------
       uris - a list of session uris
       new_project - The name of the project to which to move the sessions.
    """
    def move (self, uris, new_project):
        add_src = lambda u: urllib.urlencode({'src':u})

        async_ = len(uris) > 1 and 'true' or 'false'
        print(async_)

        post_body = '&'.join ((map(add_src,uris))
                            + [urllib.urlencode({'newProject':new_project})]
                            + [urllib.urlencode({'async':async_})])

        request_uri = '/data/services/prearchive/move?format=csv'
        return self._intf._exec(request_uri ,'POST', post_body,

                                {'content-type':'application/x-www-form-urlencoded'})
    """
    Reinspect the file on the filesystem on the XNAT server and recreate the
    parameters of the file. Essentially a refresh of the file.

    Be warned that if this session has been scheduled for an operation, that
    operation is cancelled.
    Parameters
    ----------
       uris - a list of session uris
       new_project - The name of the project to which to move the sessions.
    """
    def reset(self, triple):
        post_body = "action=build"
        request_uri = '/data/prearchive/projects/%s?format=single' \
                    % '/'.join(triple)
        return self._intf._exec(request_uri ,'POST', post_body,
                                {'content-type':'application/x-www-form-urlencoded'})
    """
    Delete  a session from the prearchive
    Parameters
    ----------
       uri - The uri of the session to delete
    """
    def delete (self, uri):
        post_body = "src=" + uri + "&" + "async=false"
        request_uri = "/data/services/prearchive/delete?format=csv"
        return self._intf._exec(request_uri ,'POST', post_body,
                                {'content-type':'application/x-www-form-urlencoded'})
    """
    Get the uri of the given session.
    Parameters
    ----------
       triple - A list containing the project, timestamp and session id, in that order.
    """
    def get_uri(self, triple):
        return JsonTable(
            self._intf._get_json('/data/prearchive/projects')
            ).where(
            project=triple[0], timestamp=triple[1], folderName=triple[2]
            ).get('url')
