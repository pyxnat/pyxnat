from __future__ import with_statement

import os
import platform
import ctypes
import glob
import hashlib
import re
import sqlite3
import time
import email
import shutil
import atexit
from fnmatch import fnmatch
from StringIO import StringIO

from ..externals import simplejson as json
from ..externals import httplib2
from ..externals import lockfile

from . import sqlutil
from .jsonutil import JsonTable, csv_to_json
from .uriutil import join_uri

_platform = platform.system()

DEBUG = False

def md5name(key):
    format = re.findall('.*?(?=(\?format=.+?(?=\?|&|$)|\&format=.+?(?=\?|&|$)))', key)
    
    if format != []:
        key = key.replace(format[0], '')
        key += format[0].split('format')[1]

    return '%s_%s'%(hashlib.md5(key).hexdigest(), key.split('/')[-1].replace('=', '.').replace('&', '_'))


class HCache(object):
    def __init__(self, cachedir, interface, safe=md5name, timer=30.0):
        self._intf = interface

        self.cache = cachedir
        self.safe = safe
        self.cachepath = None
        self._index_path = os.path.join(cachedir, 'index.json')
        self.index = {'index':{}, 'catalog':{}}
        self.timer = timer
        self.last_time = time.time()

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

        self.sync(force=True)

        atexit.register(self.sync, True)

    def sync(self, force=False):
        if time.time() - self.last_time > self.timer or force:

            start = time.time()

#            print 'sync', 

            #FIXME: will raise an error an fail when timout, put a timer for every lock
#            lock  = lockfile.FileLock(self._index_path, timeout=self.timer)
#            with lock:
            try:
                if os.path.exists(self._index_path):
                    info = json.load(open(self._index_path, 'rb'))

                    for key in info['index'].keys():
                        if not self.index['index'].has_key(key) \
                            or info['index'][key]['time'] > self.index['index'][key]['time']:
                                self.index['index'][key] = info['index'][key]

                        if info['catalog'].has_key(key) and (
                            not self.index['catalog'].has_key(key)
                            or info['catalog'][key]['time'] > self.index['catalog'][key]['time']):
                                self.index['catalog'][key] = info['catalog'][key]

            except Exception,e:
                print e

                json.dump(self.index, open(self._index_path, 'w'))

            self.last_time = time.time()
#            print time.time() - start

    def get(self, key):
        self.sync()

        retval = None
        _cachepath = self.index['catalog'].get(key, {}
                     ).get('path', os.path.join(self.cache, self.safe(key)) )

        _headerpath = os.path.join(self.cache, self.safe(key))+'.headers'

        try:
#            lock  = lockfile.FileLock(_headerpath)

#            with lock:
            f = file(_headerpath, "rb")
            retval = f.read()
            f.close()

            f = file(_cachepath, "rb")
            retval += f.read()
            f.close()
        except IOError, e:
#            print 'get cache', e
            if not self.check(key):
                self.delete(key)
            return

        return retval

    def set(self, key, value):
        timestamp = time.time()

        if self.cachepath is None:
            _cachepath = os.path.join(self.cache, self.safe(key))
            if self.index['catalog'].has_key(key):
                self.delete(key)
#                del self.index['catalog'][key]
        else:
            _cachepath = self.cachepath

            self.index['catalog'].setdefault(key, {})['path'] = _cachepath
            self.index['catalog'].setdefault(key, {})['time'] = timestamp
            self.cachepath = None

        _headerpath = os.path.join(self.cache, self.safe(key))+'.headers'

        header = ''
        value = StringIO(value)

        while len(header) < 4 or header[-4:] != '\r\n\r\n':
            header += value.read(1)

        content = value.read()

        content_type = re.findall('(?<=content-type:\s).*?(?=\r\n|$)', header)[0]

        size = len(content) + len(header) + len(content_type)

        self.index['index'].setdefault(key, {})['time'] = timestamp
        self.index['index'].setdefault(key, {})['size'] = size
        self.index['index'].setdefault(key, {})['content_type'] = content_type

        space_left = self._intf.cache.space_left()
        space_used = self._intf.cache.space_used()
        if space_left / float(space_used + space_left)* 100 < 10:
            print 'Warning: hard disk is %.2f%% full' % \
                (space_used / float(space_used + space_left) *100)

#        if space_left < size:
#            self._intf.cache.free_space(str(size - space_left)+'K')

        # write actual data from the server
#        lock  = lockfile.FileLock(_headerpath)

#        with lock:
        f = file(_headerpath, "wb")
        f.write(header)
        f.close()

        f = file(_cachepath, "wb")
        f.write(content)
        f.close()

        if _cachepath != os.path.join(self.cache, self.safe(key)) and \
            os.path.exists(os.path.join(self.cache, self.safe(key))):
                os.remove(os.path.join(self.cache, self.safe(key)))

        self.sync()

    def delete(self, key):
        _cachepath = self.index['catalog'].get(key, {}
                     ).get('path', os.path.join(self.cache, self.safe(key)) )

        _headerpath = os.path.join(self.cache, self.safe(key))+'.headers'

        if self.index['catalog'].has_key(key):
            del self.index['catalog'][key]
        if self.index['index'].has_key(key):
            del self.index['index'][key]

#        lock  = lockfile.FileLock(_headerpath)

#        with lock:
        if os.path.exists(_headerpath):
            os.remove(_headerpath)
        if os.path.exists(_cachepath):
            os.remove(_cachepath)

        self.sync(True)

    def preset(self, path):
        self.cachepath = path

    def check(self, key):
        return os.path.exists(
                self.index['catalog'].get(key, {}
                 ).get('path', os.path.join(self.cache, self.safe(key)) )
                )

    def get_default_diskpath(self, key):
        return os.path.join(self.cache, self.safe(key))

    def get_diskpath(self, key):
        return self.index['catalog'].get(key, {}
                 ).get('path', os.path.join(self.cache, self.safe(key)) )


class CacheManager(object):
    def __init__(self, interface):
        self._intf = interface
        self._cache = interface._conn.cache
        self.size_limit = None
#        self.prioritize = ''
#        self._index_path = os.path.join(cachedir, 'index.json' + '.' + str(os.getpid()) + '@' + gethostname())

    def clear(self):
        for key in self._cache.index['index'].keys():
            self._cache.delete(key)

    def free_space(self, size='1M'):
        size = memstr_to_bytes(size)
        freed = 0
        to_delete = []

        for key in self._cache.index['index'].keys():
            freed += self._cache.index['index'][key]['size']
            to_delete.append(key)

            if freed >= size:
                break

        for key in to_delete:
            self._cache.delete(key)

    def space_left(self):
        if self.size_limit is None:
            if _platform == 'Windows':
                available = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                                        ctypes.c_wchar_p(self._cache.cache),
                                        None, 
                                        None, 
                                        ctypes.pointer(available))

                return available.value
            else:
                cache_st = os.statvfs(self._cache.cache)

                return cache_st.f_bavail * cache_st.f_bsize
        else:
            return self.size_limit - self.space_used()

    def space_used(self):
        used = 0

        for key in self._cache.index['index'].keys():
            used += self._cache.index['index'][key]['size']

        return used

    def status(self):
        space_used = self.space_used()
        space_used_norm = float(space_used) / 1024**2 if float(space_used) / 1024**2 < 1024 \
                                                    else float(space_used) / 1024**3
        space_used_unit = 'M' if float(space_used) / 1024**2 < 1024 else 'G'

        space_left = self.space_left()
        space_left_norm = float(space_left) / 1024**2 if float(space_left) / 1024**2 < 1024 \
                                                    else float(space_left) / 1024**3
        space_left_unit = 'M' if float(space_left) / 1024**2 < 1000 else 'G'

        print 'used space: %s%s'%(round(space_used_norm, 2), space_used_unit)
        print 'free space: %s%s'%(round(space_left_norm, 2), space_left_unit)
        print '----------------'
        print 'U: %s%% F: %s%%'%(round(space_used*100/float(space_used+space_left), 2), 
                                 round(space_left*100/float(space_used+space_left), 2) )

    def sync(self):
        url = join_uri(self._intf._server, '/REST/subjects?format=csv&columns=ID,last_modified')

        if os.path.exists(self._cache.get_diskpath(url)):
            fp = open(self._cache.get_diskpath(url), 'rb')
            content = fp.read()
            fp.close()
            local_version = JsonTable(csv_to_json(content)).select(['ID', 'last_modified'])
            local_version.order_by = ['ID', 'last_modified']
        else:
            local_version = {}


        content = self._intf._exec('/REST/subjects?format=csv&columns=ID,last_modified')
        server_version = JsonTable(csv_to_json(content)).select(['ID', 'last_modified'])
        server_version.order_by = ['ID', 'last_modified']

        not_diff = set(local_version.items()).intersection(server_version.items())

        for key in self._cache.index['index'].keys():
            if key != url and \
                not any(subject[0] in key for subject in not_diff):
                    print entry
                    self._intf._exec(re.findall('/REST/.*', key)[0])

    def entries(self):
        return self._cache.index['index'].keys()


def memstr_to_bytes(text):
    """ Convert a memory text to it's value in kilobytes.
    """
    kilo = 1024**2
    units = dict(K=1, M=kilo, G=kilo**2)
    try:
        size = int(units[text[-1]]*float(text[:-1]))
    except (KeyError, ValueError):
        raise ValueError(
                "Invalid literal for size give: %s (type %s) should be "
                "alike '10G', '500M', '50K'." % (text, type(text))
                )
    return size



