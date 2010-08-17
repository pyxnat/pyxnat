import os
import platform
import ctypes
import glob
import hashlib
import re
from fnmatch import fnmatch
from StringIO import StringIO

from ..externals import simplejson as json
from ..externals import httplib2

_platform = platform.system()

def md5name(key):
    format = re.findall('.*?(?=(\?format=.+?(?=\?|&|$)|\&format=.+?(?=\?|&|$)))', key)
    
    if format != []:
        key = key.replace(format[0], '')
        key += format[0].split('format')[1]

    return '%s_%s'%(hashlib.md5(key).hexdigest(), key.split('/')[-1].replace('=', '.').replace('&', '_'))

class MultiCache(object):
    """Uses a local directory as a store for cached files.
       Stores the HTTP headers and body in two separate files.
    """
    def __init__(self, cache, interface, safe=md5name):
        self.cache = cache
        self.safe = safe
        self._intf = interface

        if not os.path.exists(cache): 
            os.makedirs(self.cache)

    def get(self, key):
        retval = None
        cachepath = os.path.join(self.cache, self.safe(key))

        try:
            f = file(cachepath+'.headers', "rb")
            retval = f.read()
            f.close()

            f = file(cachepath, "rb")
            retval += f.read()
            f.close()
        except IOError:
            pass
        return retval

    def set(self, key, value):
        if self._intf.cache.used() >= self._intf.cache.max_usage:
            print 'Warning: cache partition %d%% full'%self._intf.cache.used()

        cachepath = os.path.join(self.cache, self.safe(key))

        header = ''
        value = StringIO(value)

        while len(header) < 4 or header[-4:] != '\r\n\r\n':
            header += value.read(1)

        f = file(cachepath+'.headers', "wb")
        f.write(header)
        f.close()

        f = file(cachepath, "wb")
        f.write(value.read())
        f.close()

    def delete(self, key):
        cachepath = os.path.join(self.cache, self.safe(key))

        if os.path.exists(cachepath+'.headers'):
            os.remove(cachepath+'.headers')

        if os.path.exists(cachepath): 
            os.remove(cachepath)


def get_content_type(content_headers):
    return re.findall('(?<=content-type:\s).*?(?=\r\n|$)', content_headers)[0]

def get_content_uri(content_headers):
    return re.findall('content-location:\shttp.?://.*?(?=\r\n|$)', 
                      content_headers)[0].split('/REST')[1].split('?')[0]

class CacheManager(object):
    def __init__(self, interface):
        self._intf = interface
        self.max_usage = 90.0

    def __len__(self):
        return self.count()

    def clear(self):
        [os.remove(entry) for entry in glob.iglob(os.path.join(self._intf._cachedir, '*'))]

    def delete(self, uri):
        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            val = f.read()
            f.close()

            if get_content_uri(val) == uri:
                os.remove(entry)
                os.remove(entry.split('.headers')[0])

    def count(self):
        return len(self.all())

    def all(self, _filter='*'):
        uris = []

        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            val = f.read()
            f.close()
            content_uri = get_content_uri(val)
            if fnmatch(content_uri, _filter):
                uris.append(content_uri)

        return uris

    def files(self, _filter='*'):
        uris = []

        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            content_headers = f.read()
            f.close()

            if get_content_type(content_headers) != 'application/octet-stream':
                continue

            content_uri = get_content_uri(content_headers)

            if fnmatch(content_uri, _filter):
                uris.append(content_uri)

        return uris


    def resources(self, _filter='*'):
        uris = []

        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            content_headers = f.read()
            f.close()

            if get_content_type(content_headers) == 'application/octet-stream':
                continue

            content_uri = get_content_uri(content_headers)

            if fnmatch(content_uri, _filter):
                uris.append(content_uri)

        return uris

    def get_data_file(self, uri):
        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            val = f.read()
            f.close()
            if get_content_uri(val) == uri:
                return entry.split('.headers')[0]

    def content(self, uri):
        f = open(self.get_data_file(uri), 'rb')
        val = f.read()
        f.close()

        return val

    def get_header_file(self, uri):
        for entry in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            f = open(entry, 'rb')
            val = f.read()
            f.close()
            if get_content_uri(val) == uri:
                return entry

    def header(self, uri, header):
        f = open(self.get_header_file(uri), 'rb')
        val = f.read()
        f.close()

        return re.findall('(?<=%s:\s).*?(?=\r\n|$)'%header, val)[0]

    def used(self):
        if _platform == 'Windows':
            capacity = ctypes.c_ulonglong(0)
            available = ctypes.c_ulonglong(0)

            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                                    ctypes.c_wchar_p(self._intf._cachedir),
                                    None, 
                                    ctypes.pointer(capacity), 
                                    ctypes.pointer(available))

            return (capacity.value - available.value) * 100 / float(capacity.value)
        else:
            cache_st = os.statvfs(self._intf._cachedir)

            return (cache_st.f_blocks - cache_st.f_bavail) * 100 / float(cache_st.f_blocks)

