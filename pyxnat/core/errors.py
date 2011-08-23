import re

import httplib2

# parsing functions

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

def parse_put_error_message(message):
    if message.startswith('<html>'):
        error = message.split('<h3>')[1].split('</h3>')[0]

    required_fields = []

    for line in error.split('\n'):

        try:
            datatype_name = re.findall("\'.*?\'",line)[0].strip('\'')
            element_name = re.findall("\'.*?\'",line
                                      )[1].rsplit(':', 1)[1].strip('}\'')

            required_fields.append((datatype_name, element_name))
        except:
            continue

    return required_fields

def catch_error(msg_or_exception):

    # handle errors returned by the xnat server
    if isinstance(msg_or_exception, (str, unicode)):
        # parse the message
        msg = msg_or_exception

        if msg.startswith('<html>'):
            error = msg.split('<h3>')[1].split('</h3>')[0]

        elif msg.startswith('<!DOCTYPE'):
            if 'Not Found' in msg.split('<title>')[1].split('</title>')[0]:
                error = msg.split('<title>')[1].split('</title>')[0]
            else:
                error = msg.split('<h1>')[1].split('</h1>')[0]
        else:
            error = msg
            
        # choose the exception
        if error == 'The request requires user authentication':
            raise OperationalError('Authentication failed')
        elif 'Not Found' in error:
            raise OperationalError('Connection failed')
        else:
            raise DatabaseError(error)

    # handle other errors, raised for instance by the http layer
    else:
        if isinstance(msg_or_exception, httplib2.ServerNotFoundError):
            raise OperationalError('Connection failed')
        else:
            raise DatabaseError(str(msg_or_exception))


# Exceptions as defined in PEP-249, the module treats errors using thoses
# classes following as closely as possible the original definitions.

class Warning(StandardError):
    pass

class Error(StandardError):
    pass

class InterfaceError(Error):
    pass

class DatabaseError(Error):
    pass

class DataError(DatabaseError):
    pass

class OperationalError(DatabaseError):
    pass

class IntegrityError(DatabaseError):
    pass

class InternalError(DatabaseError):
    pass

class ProgrammingError(DatabaseError):
    pass

class NotSupportedError(DatabaseError):
    pass
