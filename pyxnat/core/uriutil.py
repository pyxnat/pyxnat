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
    return '/'.join(uri.split('/') + [seg.lstrip('/') for seg in segments]).rstrip('/')

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
