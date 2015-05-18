import re

from lxml import etree

# parsing functions


def is_xnat_error(message):
    return message.startswith('<!DOCTYPE') or message.startswith('<html>')


def parse_error_message(message):
    try:
        if message.startswith('<html>'):
            message_tree = etree.XML(message)
            error_tag = message_tree.find('.//h3')
            if error_tag:
                error = error_tag.xpath("string()")
        elif message.startswith('<!DOCTYPE'):
            message_tree = etree.XML(message)
            error_tag = message_tree.find('.//title')
            if error_tag and 'Not Found' in error_tag.xpath("string()"):
                error = error_tag.xpath("string()")
            else:
                error_tag = message_tree.find('.//h1')
                if error_tag:
                    error = error_tag.xpath("string()")
        else:
            error = message

    except Exception:
        error = message
    finally:
        return error


def parse_put_error_message(message):
    error = parse_error_message(message)

    required_fields = []

    if error:
        for line in error.split('\n'):

            try:
                datatype_name = re.findall("\'.*?\'", line)[0].strip('\'')
                element_name = re.findall("\'.*?\'", line
                                          )[1].rsplit(':', 1)[1].strip('}\'')

                required_fields.append((datatype_name, element_name))
            except:
                continue

    return required_fields


def catch_error(msg_or_exception, full_response=None):

    # handle errors returned by the xnat server
    if isinstance(msg_or_exception, (str, unicode)):
        # parse the message
        msg = msg_or_exception
        error = parse_error_message(msg)

        # choose the exception
        if error == 'The request requires user authentication':
            raise OperationalError('Authentication failed')
        elif 'Not Found' in error:
            raise OperationalError('Connection failed')
        else:
            if full_response:
                raise DatabaseError(full_response)
            else:
                raise DatabaseError(error)

    # handle other errors, raised for instance by the http layer
    else:
        raise DatabaseError(str(msg_or_exception))


# Exceptions as defined in PEP-249, the module treats errors using thoses
# classes following as closely as possible the original definitions.


# http://python3porting.com/differences.html#standarderror
try:
    class Warning(StandardError):
        pass

    class Error(StandardError):
        pass
except NameError:
    class Warning(Exception):
        pass

    class Error(Exception):
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
