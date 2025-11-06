import os
import time
import getpass
import json
import requests

from urllib.parse import urlparse

from .select import Select
from .help import Inspector, GraphData, PaintGraph, _DRAW_GRAPHS
from .manage import GlobalManager
from .uriutil import join_uri, file_path, uri_last
from .jsonutil import csv_to_json
from .errors import is_xnat_error
from .errors import catch_error
from .array import ArrayData
from .xpath_store import XpathStore
from . import xpass
from . import derivatives


DEBUG = False
STUBBORN = False


# generic classes
def __get_modules__(m):
    import pkgutil
    modules = []
    prefix = m.__name__ + '.'
    for importer, modname, ispkg in pkgutil.iter_modules(m.__path__, prefix):
        module = __import__(modname, fromlist='dummy')
        if not ispkg:
            modules.append(module)
        else:
            modules.extend(__get_modules__(module))
    return modules


def __find_all_functions__(m):
    import inspect
    functions = {}
    modules = __get_modules__(m)
    for m in modules:
        for name, obj in inspect.getmembers(m):
            if inspect.isfunction(obj):
                functions.setdefault(m, []).append(obj)
    return functions


# main entry point
class Interface(object):
    """ Main entry point to access an XNAT server.

        >>> central = Interface(server='http://central.xnat.org:8080',
                                user='login',
                                password='pwd')

        Or with config file:

        >>> central = Interface(config='/home/me/.xnat.cfg')

        Or for interactive use:

        >>> central = Interface('http://central.xnat.org')

        .. note::
            The interactive mode is triggered whenever an argument (between
            server, user or password) is missing. In interactive mode pyxnat
            will check that connection settings are valid.

        .. note::
            Proxy support requires the socks module be installed. This can be
            installed via pip::

            `pip install SocksiPy-branch`

        Or anonymously (unauthenticated):

        >>> central = Interface('http://central.xnat.org', anonymous=True)
    """

    def __init__(self, server=None, user=None, password=None, config=None,
                 anonymous=False, proxy=None, verify=None):
        """
            Parameters
            ----------
            server: string | None
                The server's full URL (including port and XNAT instance name
                if necessary) e.g. http://central.xnat.org,
                http://localhost:8080/xnat_db
                If None the user will be prompted for it.
            user: string | None
                A valid login registered through the XNAT web interface.
                If None the user will be prompted for it.
            password: string | None
                The user's password.
                If None the user will be prompted for it.

            config: string
                Reads a config file in json to get the connection parameters.
                If a config file is specified, it will be used regardless of
                other parameters that might have been given.
            anonymous: boolean
                Indicates an unauthenticated connection.  If True, user
                and password are ignored and a session is started with
                no credentials.
            proxy: string | None
                Indicates the full URL for an HTTP proxy server to be used for
                transactions with the specified XNAT server. If you need to
                specify a username and password for proxy access, prepend them
                to the hostname:
                http://user:pass@hostname:port

            verify: True, False, or path to file containing certificate for
              your site. Added to the requests Session, as documented here:
              http://docs.python-requests.org/en/latest/user/advanced/#ssl-cert-verification
              Simplifies handling self-certified sites, or sites where there
              is an issue with certification

        """

        self._interactive = False
        self._anonymous = anonymous
        self._verify = verify

        if self._anonymous:

            if server is None:
                self._server = input('Server: ')
                self._interactive = True
            else:
                self._server = server
                self._interactive = False

            self.__set_proxy(proxy)

            self._user = None
            self._pwd = None

        else:

            if not all([server, user, password]) and not config:
                self._interactive = True

            if all(arg is None
                    for arg in [server, user, password, config]) \
                    and os.path.exists(xpass.path()):

                connection_args = xpass.read_xnat_pass(xpass.path())

                if connection_args is None:
                    raise Exception('XNAT configuration file not found '
                                    'or formatted incorrectly.')

                self._server = connection_args['host']
                self._user = connection_args['u']
                self._pwd = connection_args['p']

                if 'proxy' in connection_args:
                    self.__set_proxy(connection_args['proxy'])
                else:
                    self.__set_proxy(None)

            elif config is not None:
                self.load_config(config)

            else:
                if server is None:
                    self._server = input('Server: ')
                else:
                    self._server = server

                if user is None:
                    user = input('User: ')

                if password is None:
                    password = getpass.getpass()

                self._user = user
                self._pwd = password

                self.__set_proxy(proxy)

        self._callback = None

        self._struct = {}
        self._entry = None
        self._jsession = None  # 'authentication_by_credentials'
        self._connect_extras = {}
        self._connect()

        self.inspect = Inspector(self)
        self.select = Select(self)
        self.array = ArrayData(self)
        self.manage = GlobalManager(self)
        self.xpath = XpathStore(self)

        functions = __find_all_functions__(derivatives)
        d = {}
        for m, mod_functions in functions.items():
            if hasattr(m, 'XNAT_RESOURCE_NAME'):
                d[m.XNAT_RESOURCE_NAME] = mod_functions
            elif hasattr(m, 'XNAT_RESOURCE_NAMES'):
                for each in m.XNAT_RESOURCE_NAMES:
                    d[each] = mod_functions
        self._mod_functions = d

        if _DRAW_GRAPHS:
            self._get_graph = GraphData(self)
            self.draw = PaintGraph(self)

        if self._interactive:
            self._get_entry_point()

        self.inspect()

    def __getstate__(self):
        return {
            '_server': self._server,
            '_user': self._user,
            '_pwd': self._pwd,
            '_anonymous': self._anonymous,
        }

    def __setstate__(self, dictionary):
        self.__dict__ = dictionary
        if self._anonymous:
            self.__init__(self._server, anonymous=True)
        else:
            self.__init__(self._server, self._user, self._pwd)

    def __set_proxy(self, proxy=None):
        if proxy is None:
            proxy = os.environ.get("http_proxy")
        if proxy is None:
            self._proxy_url = None
        else:
            self._proxy_url = urlparse(proxy)

    def _get_entry_point(self):
        if self._entry is None:
            # /REST for XNAT 1.4, /data if >=1.5
            self._entry = '/REST'
            try:
                ans = self._exec('/data/JSESSION', force_preemptive_auth=True)
                self._jsession = 'JSESSIONID=' + str(ans)
                self._entry = '/data'

                if is_xnat_error(self._jsession):
                    catch_error(self._jsession)
            except Exception as e:
                if '/data/JSESSION' not in str(e):
                    raise e

        return self._entry

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

        self._http = requests.Session()

        # requests verify defaults to True, but can be set from environment
        # variables Leave as-is unless user has explicitly overridden it
        if self._verify is not None:
            self._http.verify = self._verify

        if not self._anonymous:
            self._http.auth = (self._user, self._pwd)

        if self._proxy_url:
            self._http.proxies = {'http': self._proxy_url.geturl()}

        # Turns out this doesn't work any more: XNAT doesn't do the 401
        # response that forces httplib2 to re-submit the request with
        # credentials. See where the Authorization header is added manually in
        # the _exec function.
        # if not self._anonymous:
        #    self._http.add_credentials(self._user, self._pwd)

    def _exec(self, uri, method='GET', body=None, headers=None,
              force_preemptive_auth=False, **kwargs):
        """ A wrapper around a simple httplib2.request call that:
                - avoids repeating the server url in the request
                - deals with custom caching mechanisms :: Depricated
                - manages a user session with cookies
                - catches and broadcast specific XNAT errors

            Parameters
            ----------
            uri: string
                URI of the resource to be accessed. e.g. /REST/projects
            method: GET | PUT | POST | DELETE | HEAD
                HTTP method.
            body: string | dict
                HTTP message body
            headers: dict
                Additional headers for the HTTP request.
            force_preemptive_auth: boolean
                .. note:: Depricated as of 1.0.0.0
                Indicates whether the request should include an Authorization
                header with basic auth credentials.
            **kwargs: dictionary
                Additional parameters to pass directly to the Requests HTTP
                call.

            HTTP:GET
            ----------
                When calling with GET as method, the body parameter can be a
                key:value dictionary containing request parameters or a string
                of parameters. They will be url encoded and appended to the
                url.

            HTTP:POST
            ----------
                When calling with POST as method, the body parameter can be a
                key:value dictionary containing request parameters they will
                be url encoded and appended to the url.

        """

        if headers is None:
            headers = {}

        self._get_entry_point()

        uri = join_uri(self._server, uri)

        if DEBUG:
            print(uri)

        response = None

        def request(method, uri, headers, body, kwargs):
            if method == 'PUT':
                response = self._http.put(uri, headers=headers, data=body,
                                          **kwargs)
            elif method == 'GET':
                response = self._http.get(uri, headers=headers, params=body,
                                          **kwargs)
            elif method == 'POST':
                response = self._http.post(uri, headers=headers, data=body,
                                           **kwargs)
            elif method == 'DELETE':
                response = self._http.delete(uri, headers=headers, data=body,
                                             **kwargs)
            elif method == 'HEAD':
                response = self._http.head(uri, headers=headers, data=body,
                                           **kwargs)
            else:
                print('Unsupported HTTP method (%s)' % method)
                return
            return response

        response = request(method, uri, headers, body, kwargs)
        if response is None:
            return

        # Dirty trick to help Travis CI tests on CENTRAL: consider fixing it
        if STUBBORN:
            if (response is not None and response.status_code == 500):
                print('Retrying request... %s' % uri)
                response = request(method, uri, headers, body, kwargs)

        if (response is not None and not response.ok) or \
           is_xnat_error(response.content):
            if DEBUG:
                print(response.content)
                print(response.status_code)

            catch_error(response.content, '''pyxnat._exec failure:
                    URI: {response.url}
                    status code: {response.status_code}
                    headers: {response.headers}
                    content: {response.content}
                '''.format(response=response))

        return response.content

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

        json_content = csv_to_json(content)

        # add the (relative) path field for files
        base_uri = uri.split('?')[0]
        if uri_last(base_uri) == 'files':
            for element in json_content:
                element['path'] = file_path(element['URI'])
        return json_content

    def _get_head(self, uri):
        if DEBUG:
            print('GET HEAD')

        response = self._http.head('{server}{uri}'.format(server=self._server,
                                                          uri=uri))

        if not response.ok:
            time.sleep(1)
            self._http.head('{server}{uri}'.format(server=self._server,
                                                   uri=uri))

        return response.headers

    def save_config(self, location):
        """ Saves current configuration - including password - in a file.

            .. warning::
                Since the password is saved as well, make sure the file
                is saved at a safe location with appropriate permissions.

            .. note::
                This method raises NotImplementedError for an anonymous
                interface.

            Parameters
            ----------
            location: string
                Destination config file.
        """
        if self._anonymous:
            raise NotImplementedError(
                'no save_config() for anonymous interfaces')

        expanded_path = os.path.abspath(os.path.expanduser(location))
        if not os.path.exists(os.path.dirname(expanded_path)):
            os.makedirs(os.path.dirname(expanded_path))

        config = {'server': self._server,
                  'user': self._user,
                  'password': self._pwd,
                  }
        if self._verify is not None:
            config['verify'] = self._verify

        if self._proxy_url:
            config['proxy'] = self._proxy_url.geturl()

        with open(expanded_path, 'w') as fp:
            json.dump(config, fp)

    def load_config(self, location):
        """ Loads a configuration file and replaces current connection
            parameters.

            .. note::
                This method raises NotImplementedError for an anonymous
                interface.

            Parameters
            ----------
            location: string
                Configuration file path.
        """
        if self._anonymous:
            raise NotImplementedError(
                'no load_config() for anonymous interfaces')

        if os.path.exists(location):
            with open(location, 'rb') as fp:
                config = json.load(fp)

            self._server = str(config['server'])
            self._user = str(config['user'])
            self._pwd = str(config['password'])

            self._verify = bool(config.get('verify', True))
            if 'proxy' in config:
                self.__set_proxy(str(config['proxy']))
            else:
                self.__set_proxy(None)

        else:
            raise Exception('Configuration file does not exist.')

    def version(self):
        """
            Get version of the currently running XNAT instance.
        """
        from pyxnat.core.errors import DatabaseError
        try:
            return self._exec('/data/version')
        except DatabaseError:
            j = self._exec('/xapi/siteConfig/buildInfo').decode()
            return json.loads(j)

    def set_logging(self, level=0):
        pass

    def disconnect(self):
        """
            Tell XNAT to disconnect this session
        """
        self._exec('/data/JSESSION', method='DELETE')
        self._http.close()

    def get(self, uri, **kwargs):
        '''
        Wrapper around requests.get()
        returns rquests.response object
        '''
        uri = join_uri(self._server, uri)
        response = self._http.get(uri, **kwargs)
        return response

    def put(self, uri, **kwargs):
        '''
        Wrapper around requests.put()
        returns rquests.response object
        '''
        uri = join_uri(self._server, uri)
        response = self._http.put(uri, **kwargs)
        return response

    def post(self, uri, **kwargs):
        '''
        Wrapper around requests.post()
        returns rquests.response object
        '''
        uri = join_uri(self._server, uri)
        response = self._http.post(uri, **kwargs)
        return response

    def delete(self, uri, **kwargs):
        '''
        Wrapper around requests.delete()
        returns rquests.response object
        '''
        uri = join_uri(self._server, uri)
        response = self._http.delete(uri, **kwargs)
        return response

    def head(self, uri, **kwargs):
        '''
        Wrapper around requests.head()
        returns rquests.response object
        '''
        uri = join_uri(self._server, uri)
        response = self._http.head(uri, **kwargs)
        return response

    def __enter__(self):

        return self

    def close_jsession(self):
        '''
        Closes the session with XNAT server and consumes the JSESSIONID token.
        '''
        uri = '/data/JSESSION'
        response = self.delete(uri)
        response.raise_for_status()
        self._jsession = None

    def __exit__(self, type, value, traceback):

        if self._jsession:
            self.close_jsession()
        self._http.close()
