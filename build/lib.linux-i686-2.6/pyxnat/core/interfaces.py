import os
import time
import tempfile
import email
import getpass

from ..externals import httplib2

from .select import Select
from .cache import CacheManager, MultiCache
from .search import SearchManager
from .help import Inspector
from .users import Users

from .uriutil import join_uri
from .jsonutil import csv_to_json


DEBUG = False

# main entry point
class Interface(object):
    """ Main entry point to access a XNAT server.

        >>> central = Interface(server='http://central.xnat.org:8080',
                                user='login',
                                password='pwd',
                                cachedir='/tmp'
                                )

        Attributes
        ----------
        _mode: online | offline
            Online or offline mode
        _memlifespan: float
            Lifespan of in-memory cache
    """

    def __init__(self, server, user=None, password=None, 
                                          cachedir=tempfile.gettempdir()):
        """ 
            Parameters
            ----------
            server: string
                The server full URL (including port and XNAT instance name if necessary)
                e.g. http://central.xnat.org, http://localhost:8080/xnat_db
            user: string | None
                A valid login registered through the XNAT web interface.
                If None the user will be prompted for it.
            password: string | None
                The user's password.
                If None the user will be prompted for it.
            cachedir: string
                Path of the cache directory (for all queries and downloaded files)
                If no path is provided, a platform dependent temp dir is used.
        """

        self._server = server
        self._interactive = user is None or password is None

        if user is None:
            user = raw_input('User:')

        if password is None:
            password = getpass.getpass()

        self._user = user
        self._pwd = password

        self._cachedir = os.path.join(cachedir, 
                                      '%s@%s'%(self._user,
                                               self._server.split('//')[1].replace('/', '.')
                                               ))
        self._callback = None

        self._memcache = {}
        self._memlifespan = 1.0
        self._mode = 'online'

        self._jsession = 'authentication_by_credentials'
        self._connect()

        self.search = SearchManager(self)
        self.inspect = Inspector(self)
        self.select = Select(self)
        self.users = Users(self)
        self.cache = CacheManager(self)

        if self._interactive:
            try:
                self._jsession = self._exec('/REST/JSESSION')
            except:
                raise Exception('Wrong login or password.')

    def global_callback(self, func=None):
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
            >>> interface.global_callback(notify)
        """
        self._callback = func

    def _connect(self):
        """ Sets up the connection with the XNAT server.
        """

        if DEBUG:   
            httplib2.debuglevel = 2
        self._conn = httplib2.Http(MultiCache(self._cachedir, self))
        self._conn.add_credentials(self._user, self._pwd)

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

        uri = join_uri(self._server, uri)
 
        # using session authentication
        headers['cookie'] = self._jsession

        # reset the memcache when something is changed on the server
        if method in ['PUT', 'DELETE']:
            self._memcache = {}

        if self._mode == 'online' and method == 'GET':
            if time.time() - self._memcache.get(uri, 0) < self._memlifespan:
                if DEBUG:
                    print 'send: GET CACHE %s'%uri
                info, content = self._conn.cache.get(uri).split('\r\n\r\n')
                self._memcache[uri] = time.time()
                response = None
            else:
                response, content = self._conn.request(uri, method, body, headers)
                self._memcache[uri] = time.time()

        elif self._mode == 'offline' and method == 'GET':
            cached_value = self._conn.cache.get(uri)
            if cached_value is not None:
                if DEBUG:
                    print 'send: GET CACHE %s'%uri
                info, content = cached_value.split('\r\n\r\n')
                response = None
            else:
                try:
                    self._conn.timeout = 10
                    response, content = self._conn.request(uri, method, 
                                                           body, headers)
                    self._conn.timeout = None
                    self._memcache[uri] = time.time()
                except Exception, e:
                    raise Exception('Resource not available (it is not '
                                    'in cache and the server is unresponsive)')
        else:
            response, content = self._conn.request(uri, method, body, headers)

        if DEBUG:
            if response is None:
                response = httplib2.Response(email.message_from_string(info))
                print 'reply: %s %s from cache'%(response.status, response.reason)
                for key in response.keys():
                    print 'header: %s: %s'%(key.title(), response.get(key))

        if response is not None and response.has_key('set-cookie'):
            self._jsession = response.get('set-cookie')[:44]

        if content.startswith('<html>'):
            raise Exception(content.split('<h3>')[1].split('</h3>')[0])

        return content

    def _get_json(self, uri):
        """ Specific Interface._exec method to retrieve data.
            It forces the data format to csv and then puts it back to a json-like
            format.
            
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

        return csv_to_json(self._exec(uri, 'GET'))


