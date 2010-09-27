from ..externals import httplib2

def is_xnat_error(message):
    return message.startswith('<!DOCTYPE') or message.startswith('<html>')

def parse_error_message(message):
    if message.startswith('<html>'):
        error = message.split('<h3>')[1].split('</h3>')[0]
    elif message.startswith('<!DOCTYPE'):
        if 'Not Found' in message.split('<title>')[1].split('</title>')[0]:
           error = message.split('<title>')[1].split('</title>')[0]
        else:
            error = message.split('<h1>')[1].split('</h1>')[0]
    else:
        error = message

    return error

def raise_exception(message_or_exception):
    # handle errors returned by the xnat server
    if isinstance(message_or_exception, (str, unicode)):
        error = parse_error_message(message_or_exception)
    
        if error == 'The request requires user authentication':
            raise XnatAuthenticationError()
        elif 'Not Found' in error:
            raise XnatServerNotFoundError('Unable to find the server')
        else:
            raise BaseXnatError(error)

    # handle other errors, raised for instance by the http layer
    else:
        if isinstance(message_or_exception, httplib2.ServerNotFoundError):
            raise XnatServerNotFoundError(message_or_exception.message)
        else:
            raise BaseXnatError(message_or_exception.message)

class BaseXnatError(Exception):
    def __init__(self, message):
        self.error = message

    def __str__(self):
       return repr(self.error)

class XnatAuthenticationError(BaseXnatError):
    def __init__(self):
        BaseXnatError.__init__(self, 'Invalid login or password')

class XnatServerNotFoundError(BaseXnatError):
    def __init__(self, message):
        BaseXnatError.__init__(self, message)

class XnatSearchNotFoundError(BaseXnatError):
    def __init__(self, name):
        BaseXnatError.__init__(self, "Search '%s' not found"%name)

class BasePyxnatError(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

class PathSyntaxError(BasePyxnatError):
    def __init__(self, path):
        BasePyxnatError.__init__(self, "Invalid syntax in '%s'"%path)

class SearchShareModeError(BasePyxnatError):
    def __init__(self, share_mode):
        raise Exception("Unknown mode '%s'"%share_mode)

class RpnSyntaxError(BasePyxnatError):
    def __init__(self, expression):
        BasePyxnatError.__init__(self, "Invalid syntax in '%s'"%expression)

class ResourceConcurrentAccessError(BasePyxnatError):
    def __init__(self, pid1, pid2, uri):
        BasePyxnatError.__init__(self, 
            ('Multiple processes <%s,%s> are trying to access '
             'the same resource: %s'%(pid1, pid2, uri)
            )
        )
    

