import re

from .schema import rest_translation

def translate_uri(uri):
    segs = uri.split('/')
    for key in rest_translation.keys():
        if key in segs[-2:]:
            uri = uri.replace(key, rest_translation[key])

    return uri

def inv_translate_uri(uri):
    inv_table = dict(zip(rest_translation.values(), rest_translation.keys()))

    for key in inv_table.keys():
            uri = uri.replace(key, inv_table[key])

    return uri

def join_uri(uri, *segments):
    return '/'.join(uri.split('/') + \
                        [seg.lstrip('/') for seg in segments]).rstrip('/')

def uri_last(uri):
    return uri.split('/')[-1]

def uri_nextlast(uri):
    return uri.split('/')[-2]

def uri_parent(uri):
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
