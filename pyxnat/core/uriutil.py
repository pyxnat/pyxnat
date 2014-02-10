import os
import re

from .schema import rest_translation
# from .schema import resources_types

def translate_uri(uri):
    segs = uri.split('/')
    for key in rest_translation.keys():
        if key in segs[-2:]:
            uri = uri.replace(key, rest_translation[key])

    return uri

def inv_translate_uri(uri):
    inv_table = dict(zip(rest_translation.values(), rest_translation.keys()))

    for key in inv_table.keys():
            uri = uri.replace('/%s' % key, '/%s' % inv_table[key])

    return uri

def join_uri(uri, *segments):
    return '/'.join(uri.split('/') + \
                        [seg.lstrip('/') for seg in segments]).rstrip('/')

def uri_last(uri):
    # return uri.split(uri_parent(uri))[1].strip('/')
    return uri.split('/')[-1]

def uri_nextlast(uri):
    # return uri_last(uri.split(uri_last(uri))[0].strip('/'))
    # support files in a hierarchy
    if '/files/' in uri:
        return 'files'
    return uri.split('/')[-2]

def uri_parent(uri):
    # parent = uri

    # if not os.path.split(uri)[1] in resources_types:
    #     while os.path.split(parent)[1] not in resources_types:
    #         parent = os.path.split(parent)[0]

    #     return parent

    # support files in a hierarchy by stripping all but one level
    files_index = uri.find('/files/')
    if files_index >= 0:
        uri = uri[:7+files_index]
    return uri_split(uri)[0]

def uri_grandparent(uri):
    return uri_parent(uri_parent(uri))

def uri_split(uri):
    return uri.rsplit('/', 1)

def uri_segment(uri, start=None, end=None):
    if start is None and end is None:
        return uri
    elif start is None:
        return '/'+'/'.join(uri.split('/')[:end])
    elif end is None:
        return '/'+'/'.join(uri.split('/')[start:])
    else:
        return '/'+'/'.join(uri.split('/')[start:end])

def uri_shape(uri):

    kwid_map = dict(zip(uri.split('/')[1::2], uri.split('/')[2::2]))
    shapes = {}

    for kw in kwid_map:
        seps = kwid_map[kw]

        for char in re.findall('[a-zA-Z0-9]', seps):
            seps = seps.replace(char, '')

            chunks = []
            for chunk in re.split('|'.join(seps), kwid_map[kw]):
                try:
                    float(chunk)
                    chunk = '*'
                except:
                    pass

                chunks.append(chunk)

            shapes[kw] = '?'.join(chunks)

    return make_uri(shapes)

def make_uri(_dict):
    uri = ''

    kws = ['projects', 'subjects', 'experiments', 'assessors',
            'reconstructions', 'scans', 'resources', 'in_resources',
                'out_resources', 'files', 'in_files', 'out_files']

    for kw in kws:
        if _dict.has_key(kw):
            uri += '/%s/%s' % (kw, _dict.get(kw))

    return uri

def check_entry(func):
    def inner(*args, **kwargs):
        args[0]._intf._get_entry_point()
        return func(*args, **kwargs)

    return inner


def extract_uri(uri) :
    """
    Destructure the given REST uri into project,subject and experiment.

    Returns None if any one of project,subject or experiment is unspecified in the URI and a
    (project,subject,experiment) triple otherwise.
    """
    # elements in URLs are always separated by /, regardless of client
    split = uri.split('/')
    # a well qualified uri has a project subject, and experiment name
    # so when split the following items should be present:
    # ['', 'data', 'projects', 'project-name', 'subjects', 'subject-name', 'experiments', 'experiment-name', 'scans']

    # Based on the above comment if there aren't 9 items in the split list the uri isn't well qualified
    if (len(split) != 9): return None

    project = split[3]
    subject = split[5]
    experiment = split[7]

    return (project,subject,experiment)

def file_path(uri):
    """return the relative path of the file in the given URI

    for uri = '/.../files/a/b/c', return 'a/b/c'

    raises ValueError (through .index()) if '/files/' is not in the URI
    """
    return uri[7+uri.index('/files/'):]

