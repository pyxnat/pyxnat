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

from .jsonutil import JsonTable, csv_to_json
from .uriutil import join_uri

_platform = platform.system()

DEBUG = False


def md5name(key):
    format = re.findall('.*?(?=(\?format=.+?(?=\?|&|$)|'
                        '\&format=.+?(?=\?|&|$)))', key)
    
    if format != []:
        key = key.replace(format[0], '')
        key += format[0].split('format')[1]

    return '%s_%s' % (hashlib.md5(key).hexdigest(), 
                      key.split('/')[-1].replace('=', '.').replace('&', '_')
                      )


class HTCache(object):
    def __init__(self, cachedir, interface, safe=md5name):
        self._intf = interface
        
        self.cache = cachedir
        self.safe = safe

        self._cachepath = None

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

    def get(self, key):
        retval = None

        _cachepath = os.path.join(self.cache, self.safe(key))
        _headerpath = '%s.headers' % _cachepath
        
        try:
            f = file('%s.headers' % _cachepath, "rb")
            retval = f.read()
            f.close()

            f = file(_cachepath, "rb")
            retval += f.read()
            f.close()
        except IOError, e:
            try:
                f = file('%s.alt' % _cachepath, "rb")
                _altpath = f.read()
                f.close()

                f = file(_altpath, "rb")
                retval += f.read()
                f.close()
            except IOError, e:
                return

        return retval

    def set(self, key, value):
        _fakepath = '%s.alt' % os.path.join(self.cache, self.safe(key))
        _headerpath = '%s.headers' % os.path.join(self.cache, self.safe(key))
        _cachepath = os.path.join(self.cache, self.safe(key))

        if self._cachepath is not None: # when using custom path
            if _cachepath != self._cachepath and os.path.exists(_cachepath):
                os.remove(_cachepath) # remove default file if exists

            if os.path.exists(_fakepath):
                f = file(_fakepath, "rb")
                _altpath = f.read()
                f.close()
                
                if _altpath != self._cachepath and os.path.exists(_altpath):
                    # remove old custom file if different location
                    os.remove(_altpath)

            _cachepath = self._cachepath

            f = open(_fakepath, 'w')
            f.write(_cachepath)
            f.close()

            self._cachepath = None

        else:                   # when using default cache path
            if os.path.exists(_fakepath): # if alternate location exists
                f = file(_fakepath, "rb")
                _altpath = f.read()
                f.close()
                
                if _altpath != self._cachepath and os.path.exists(_altpath):
                    os.remove(_altpath) # remove actual file

                os.remove(_fakepath) # remove pointer file

        header = ''
        value = StringIO(value)

        # maybe include some kind of timer to avoid checking all the time
        disk_status = self._intf.cache.disk_ready(_cachepath)

        if not disk_status[0]:
            print 'Warning: %s is %.2f%% full' % \
                (os.path.dirname(_cachepath), disk_status[1])

        while len(header) < 4 or header[-4:] != '\r\n\r\n':
            header += value.read(1)

        content = value.read()

        f = file(_headerpath, "wb")
        f.write(header)
        f.close()

        f = file(_cachepath, "wb")
        f.write(content)
        f.close()

    def preset(self, path):
        self._cachepath = path

    def delete(self, key, value):
        _cachepath = os.path.join(self.cache, self.safe(key))
        _fakepath = '%s.alt' % _cachepath
        _headerpath = '%s.headers' % _cachepath

        if os.path.exists(_fakepath):
            f = file(_fakepath, "rb")
            _altpath = f.read()
            f.close()

            os.remove(_fakepath)
            if os.path.exists(_altpath):
                os.remove(_altpath)

        if os.path.exists(_cachepath):
            os.remove(_cachepath)

        if os.path.exists(_headerpath):
            os.remove(_headerpath)

    def get_diskpath(self, key):
        _cachepath = os.path.join(self.cache, self.safe(key))
        _fakepath = '%s.alt' % _cachepath

        if os.path.exists(_fakepath):
            f = file(_fakepath, "rb")
            _altpath = f.read()
            f.close()
            return _altpath
        else:
            return _cachepath


class CacheManager(object):
    def __init__(self, interface):
        self._intf = interface
        self._cache = interface._conn.cache

    def clear(self):
        for _fakepath in glob.iglob('%s/*.alt' % self._cache.cache):
            f = file(_fakepath, "rb")
            _altpath = f.read()
            f.close()
            
            if os.path.exists(_altpath):
                os.remove(_altpath)

        shutil.rmtree(self._cache.cache)
        os.makedirs(self._cache.cache)

    def size(self, unit='bytes'):
        """ Returns the amount of space taken by the cache.

            Parameters
            ----------
            unit: str
                unit in which to return the size
                can be bytes (default), mega or giga

            Return
            ------
            size: float
        """
        size = 0

        for cachefile in glob.iglob('%s/*' % self._cache.cache):
            size += os.path.getsize(cachefile)

            if cachefile.endswith('.alt'):
                f = file(cachefile, "rb")
                _altpath = f.read()
                f.close()

                if os.path.exists(_altpath):
                    size += os.path.getsize(_altpath)

        return bytes_to_human(size, unit)

    def available_disk(self, path, unit='bytes'):
        if not os.path.isdir(path):
            path = os.path.dirname(path.rstrip('/'))

        if _platform == 'Windows':
            available = ctypes.c_ulonglong(0)

            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                None, 
                None, 
                ctypes.pointer(available))

            return bytes_to_human(available.value, unit)
        else:
            cache_st = os.statvfs(path)

            return bytes_to_human(cache_st.f_bavail * cache_st.f_bsize, unit)

    def used_disk(self, path, unit='bytes'):
        return self.total_disk(path, unit) - self.available_disk(path, unit)

    def total_disk(self, path, unit='bytes'):
        if not os.path.isdir(path):
            path = os.path.dirname(path.rstrip('/'))

        if _platform == 'Windows':
            total = ctypes.c_ulonglong(0)

            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p(path),
                None, 
                ctypes.pointer(total),
                None,
                )

            return bytes_to_human(total.value, unit)
        else:
            cache_st = os.statvfs(path)

            return bytes_to_human(cache_st.f_blocks * cache_st.f_bsize, unit)

    def disk_ready(self, path, ready_ratio=90.0):
        disk_ratio = ( float(self.used_disk(path)) / \
                           float(self.total_disk(path)) * 100
                       )

        return disk_ratio < ready_ratio, disk_ratio


def bytes_to_human(size, unit):
    if unit == 'mega':
        return float(size) / 1024 ** 2
    elif unit == 'giga':
        return float(size) / 1024 ** 3
    else:
        return size

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



