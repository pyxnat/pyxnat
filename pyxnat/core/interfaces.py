import os
import time
import tempfile
import email
import getpass

from ..externals import httplib2
from ..externals import simplejson as json

from .select import Select
from .cache import CacheManager, HTCache
from .help import Inspector, GraphData, PaintGraph, _DRAW_GRAPHS
from .manage import GlobalManager
from .uriutil import join_uri
from .jsonutil import csv_to_json
from .errors import is_xnat_error
from .errors import catch_error

DEBUG = False

# main entry point
class Interface(object):
    """ Main entry point to access a XNAT server.

        >>> central = Interface(server='http://central.xnat.org:8080',
                                user='login',
                                password='pwd',
                                cachedir='/tmp'
                                )

        Or with config file:

        >>> central = Interface(config='/home/me/.xnat.cfg')

        Or for interactive use:

        >>> central = Interface('http://central.xnat.org')

        .. note::
            The interactive mode is activated whenever an argument within
            server, user or password is missing. In interactive mode pyxnat
            tries to check the validity of the connection parameters.
        
        Attributes
        ----------
        _mode: online | offline
            Online or offline mode
        _memtimeout: float
            Lifespan of in-memory cache
    """

    def __init__(self, server=None, user=None, password=None, 
                 cachedir=tempfile.gettempdir(), config=None):
        """ 
            Parameters
            ----------
            server: string | None
                The server full URL (including port and XNAT instance name
                if necessary) e.g. http://central.xnat.org, 
                http://localhost:8080/xnat_db
                Or a path to an existing config file. In that case the other
                parameters (user etc..) are ignored if given.
                If None the user will be prompted for it.
            user: string | None
                A valid login registered through the XNAT web interface.
                If None the user will be prompted for it.
            password: string | None
                The user's password.
                If None the user will be prompted for it.
            cachedir: string
                Path of the cache directory (for all queries and 
                downloaded files)
                If no path is provided, a platform dependent temp dir is 
                used.
v           config: string
               Reads a config file in json to get the connection parameters.
               If a config file is specified, it will be used regardless of
               other parameters that might have been given.
        """

        self._interactive = not all([server, user, password]) and not config

        if config is not None:
            self.load_config(config)
        else:
            if server is None:
                self._server = raw_input('Server: ')
            else:
                self._server = server

            if user is None:
                user = raw_input('User: ')

            if password is None:
                password = getpass.getpass()

            self._user = user
            self._pwd = password

            self._cachedir = os.path.join(
                cachedir, '%s@%s' % (
                    self._user, 
                    self._server.split('//')[1].replace(
                        '/', '.').replace(':', '_')
                    )
                )
        
        self._callback = None

        self._memcache = {}
        self._memtimeout = 1.0
        self._mode = 'online'
        self._struct = {}
        self._entry = None

        self._last_memtimeout = 1.0
        self._last_mode = 'online'

        self._jsession = 'authentication_by_credentials'
        self._connect_extras = {}
        self._connect()

        self.inspect = Inspector(self)
        self.select = Select(self)
        self.cache = CacheManager(self)
        self.manage = GlobalManager(self)
        
        if _DRAW_GRAPHS:
            self._get_graph = GraphData(self)
            self.draw = PaintGraph(self)

        if self._interactive:
            self._get_entry_point()
            self._jsession = self._exec('%s/JSESSION' % self._entry)
            if is_xnat_error(self._jsession):
                catch_error(self._jsession)

        self.inspect()

    def _get_entry_point(self):
        if self._entry is None:
            # /REST for XNAT 1.4, /data if >=1.5
            self._entry = '/REST'
            try:
                self._exec('/data/JSESSION', 'HEAD')
                self._entry = '/data'
            except:
                pass
            
    def _connect(self, **kwargs):
        """ Sets up the connection with the XNAT server.

            Parameters
            ----------
            kwargs: dict
                Can be used to pass additional arguments to
                the Http constructor. See the httplib2 documentation
                for details. http://code.google.com/p/httplib2/
        """

        if kwargs != {}:
            self._connect_extras = kwargs
        else:
            kwargs = self._connect_extras
        
        if DEBUG:   
            httplib2.debuglevel = 2
        self._http = httplib2.Http(HTCache(self._cachedir, self), **kwargs)
        self._http.add_credentials(self._user, self._pwd)

    def _exec(self, uri, method='GET', body=None, headers=None):
        """ A wrapper around a simple httplib2.request call that:
                - avoids repeating the server url in the request
                - deals with custom caching mechanisms
                - manages a user session with cookies
                - catches and broadcast specific XNAT errors

            Parameters
            ----------
            uri: string
                URI of the resource to be accessed. e.g. /REST/projects
            method: GET | PUT | POST | DELETE
                HTTP method.
            body: string
                HTTP message body
            headers: dict
                Additional headers for the HTTP request.
        """

        if headers is None:
            headers = {}

        self._get_entry_point()

        uri = join_uri(self._server, uri)

        # using session authentication
        headers['cookie'] = self._jsession
        headers['connection'] = 'keep-alive'

        # reset the memcache when client changes something on the server
        if method in ['PUT', 'DELETE']:
            self._memcache = {}
        
        if self._mode == 'online' and method == 'GET':

            if time.time() - self._memcache.get(uri, 0) < self._memtimeout:
                if DEBUG:
                    print 'send: GET CACHE %s' % uri

                info, content = self._http.cache.get(uri
                                                     ).split('\r\n\r\n', 1)

                self._memcache[uri] = time.time()
                response = None
            else:
                response, content = self._http.request(uri, method, 
                                                       body, headers)
                self._memcache[uri] = time.time()

        elif self._mode == 'offline' and method == 'GET':

            cached_value = self._http.cache.get(uri)

            if cached_value is not None:
                if DEBUG:
                    print 'send: GET CACHE %s' % uri
                info, content = cached_value.split('\r\n\r\n', 1)
                response = None
            else:
                try:
                    self._http.timeout = 10

                    response, content = self._http.request(uri, method, 
                                                           body, headers)

                    self._http.timeout = None
                    self._memcache[uri] = time.time()
                except Exception, e:
                    catch_error(e)
        else:
            response, content = self._http.request(uri, method, 
                                                   body, headers)

        if DEBUG:
            if response is None:
                response = httplib2.Response(email.message_from_string(info))
                print 'reply: %s %s from cache' % (response.status, 
                                                   response.reason
                                                   )
                for key in response.keys():
                    print 'header: %s: %s' % (key.title(), response.get(key))

        if response is not None and response.has_key('set-cookie'):
            self._jsession = response.get('set-cookie')[:44]

        if response is not None and response.get('status') == '404':
            r,_ = self._http.request(self._server)

            if self._server.rstrip('/') != r.get('content-location', 
                                                 self._server).rstrip('/'):
                
                old_server = self._server
                self._server = r.get('content-location').rstrip('/')
                return self._exec(uri.replace(old_server, ''), method, body)
            else:
                raise httplib2.HttpLib2Error('%s %s %s' % (uri, 
                                                           response.status,
                                                           response.reason
                                                           )
                                             )

        return content


    def _get_json(self, uri):
        """ Specific Interface._exec method to retrieve data.
            It forces the data format to csv and then puts it back to a 
            json-like format.
            
            Parameters
            ----------
            uri: string
                URI of the resource to be accessed. e.g. /REST/projects

            Returns
            -------
            List of dicts containing the results
        """
        if 'format=json' in uri:
            uri = uri.replace('format=json', 'format=csv')
        else:
            if '?' in uri:
                uri += '&format=csv'
            else:
                uri += '?format=csv'

        content = self._exec(uri, 'GET')

        if is_xnat_error(content):
            catch_error(content)

        return csv_to_json(content)

    def _get_head(self, uri):
        print 'GET HEAD'
        _nocache = httplib2.Http()
        _nocache.add_credentials(self._user, self._pwd)

        rheaders = {'cookie':self._jsession}

        try:
            head = _nocache.request(
                '%s%s' % (self._server, uri), 'HEAD', headers=rheaders)[0]
        except:
            time.sleep(1)
            head = _nocache.request(
                '%s%s' % (self._server, uri), 'HEAD', headers=rheaders)[0]

        info = email.Message.Message()

        for key, value in head.iteritems():
            if key == 'content-disposition':
                info['content-location'] = '%s%s' % (self._server, uri)
            if key not in ['set-cookie']:
                info[key] = value

        return info

    def save_config(self, location):
        """ Saves current configuration - including password - in a file.

            .. warning::
                Since the password is saved as well, make sure the file
                is saved at a safe location with appropriate permissions.

            Parameters
            ----------
            location: string
                Destination config file.
        """
        if not os.path.exists(os.path.dirname(location)):
            os.makedirs(os.path.dirname(location))

        fp = open(location, 'w')
        config = {'server':self._server, 
                  'user':self._user, 
                  'password':self._pwd,
                  'cachedir':self._cachedir,
                  }

        json.dump(config, fp)
        fp.close()

    def load_config(self, location):
        """ Loads a configuration file and replaces current connection
            parameters.

            Parameters
            ----------
            location: string
                Configuration file path.
        """

        if os.path.exists(location):
            fp = open(location, 'rb')
            config = json.load(fp)
            fp.close()

            self._server = config['server']
            self._user = config['user']
            self._pwd = config['password']
            self._cachedir = config['cachedir']

#     def grab(self, datatype, seq_type=None):
#         columns = []
#         if datatype.endswith('ScanData'):
#             columns = ['%s/%s' % (datatype, field)
#                        for field in ['type', 'ID', 'image_session_ID']
#                        ]
# #        else:
# #            columns = ['%s/%s'%(datatype, field) for field in ['type', 'ID', 'session_id']]
#         try:
#             data = self.select(datatype, columns).all()
#         except:
#             data = self.select(datatype).all()

#         print data.headers()

#         uris = []

#         type_header = difflib.get_close_matches('type', data.headers())

#         if difflib.get_close_matches('id', data.headers()) == []:
#             session_header = difflib.get_close_matches('session_id', 
#                                                        data.headers())[0]

#             subject_header = difflib.get_close_matches('subject_id', 
#                                                        data.headers())[0]

#             project_header = difflib.get_close_matches('project', 
#                                                        data.headers())[0]


#             print project_header, subject_header, session_header

#             for entry in data:
#                 if seq_type is None \
#                         or type_header == [] \
#                         or entry[type_header[0]] == seq_type:

#                     uris.append('/REST/projects/%s'
#                                 '/subjects/%s'
#                                 '/experiments/%s' % \
#                                     (entry[project_header],
#                                      entry[subject_header],
#                                      entry[session_header]
#                                      )
#                                 )

#         else:
#             id_header = difflib.get_close_matches('id', data.headers())[0]
#             session_header = difflib.get_close_matches('session_id', \
#                                                            data.headers())[0]

#             for entry in data:
#                 if (seq_type is None 
#                     or type_header == []
#                     or entry[type_header[0]] == seq_type
#                     ):
                    
#                     uris.append('/REST/experiments/%s/scans/%s' % \
#                                     (entry[session_header], 
#                                      entry[id_header]
#                                      )
#                                 )

#         return CObject(uris, self)
