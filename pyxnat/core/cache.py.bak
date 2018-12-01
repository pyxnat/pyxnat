from __future__ import with_statement

import os
import platform
import ctypes
import glob
import hashlib
import re
import time
import shutil
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


_platform = platform.system()

DEBUG = False


def md5name(key):
    """ Generates a unique path to store server responses.
    """
    return hashlib.md5(key).hexdigest()

def bytes_to_human(size, unit):
    """ Returns a more human readable version of a size in bytes.
    """

    if unit == 'mega':
        return float(size) / 1024 ** 2
    elif unit == 'giga':
        return float(size) / 1024 ** 3
    else:
        return size

def memstr_to_bytes(text):
    """ Convert a memory text to its value in kilobytes.
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


class HTCache(object):
    def __init__(self, cachedir, interface, safe=md5name):
        """
            Parameters
            ----------
            cachedir: string
                The cache path.
            interface:
                :class:`Interface` Object
            safe: callable
                The function used to generate the responses cache paths.
        """
        self._intf = interface

        self.cache = cachedir
        self.safe = safe

        self._cachepath = None

        if not os.path.exists(cachedir):
            os.makedirs(cachedir)

    def get(self, key):
        retval = None

        _cachepath = os.path.join(self.cache, self.safe(key))

        if DEBUG:
            print('cache get:', key,)
            print('\n\t', _cachepath)

        try:
            f = file('%s.headers' % _cachepath, "rb")
            retval = f.read()
            f.close()

            f = file(_cachepath, "rb")
            retval += f.read()
            f.close()
        except IOError:
            try:
                f = file('%s.alt' % _cachepath, "rb")
                _altpath = f.read()
                f.close()

                f = file(_altpath, "rb")
                retval += f.read()
                f.close()
            except:
                return

        return retval

    def set(self, key, value):
        """ Sets cache entry.
        """

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

            if DEBUG:
                print('cache set custom:', key)
                print('\n\t', _cachepath)

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

            if DEBUG:
                print('cache set default:', key)
                print('\n\t', _cachepath)

        header = ''
        value = StringIO(value)

        # avoid checking disk status each time
        if time.gmtime(time.time())[5] % 10 == 0:
            disk_status = self._intf.cache.disk_ready(_cachepath)

            if not disk_status[0] and self._intf.cache._warn:
                print('Warning: %s is %.2f%% full') % \
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
        """ Sets and forces a path for the next entry to be set.

            .. note::
                 Basically it is a way to trick the cache mechanism
                 into using something else than the default path to
                 store entries.
        """
        if self._intf._mode != 'offline':
            self._cachepath = path

    def delete(self, key):
        """ Deletes the entry.
        """

        if DEBUG:
            print('cache del:', key)

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

    def get_diskpath(self, key, force_default=False):
        """ Gets the disk path where the entry is stored (default path
            or not)
        """
        _cachepath = os.path.join(self.cache, self.safe(key))
        _fakepath = '%s.alt' % _cachepath

        if os.path.exists(_fakepath) and not force_default:
            f = file(_fakepath, "rb")
            _altpath = f.read()
            f.close()
            return _altpath
        else:
            return _cachepath


class CacheManager(object):
    """ Management interface for the cache.

        It provides a few methods to::
            - evaluate the size a the cache
            - check if there is space left on the disk
            - clear the cache
            - define cache usage parameters
    """
    def __init__(self, interface):
        """
            Parameters
            ----------
            interface:
                :class:`Interface` Object

        """
        self._intf = interface
        self._cache = interface._http.cache
        self._warn = True

    def enable_warnings(self, toggle=True):
        self._warn = toggle

    def clear(self):
        """ Clears all files tracked by pyxnat.
        """
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

            Returns
            -------
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

    def available_disk(self, path=None, unit='bytes'):
        """ Available disk on partition. Default location is cache folder.
        """
        if path is None:
            path = self._cache.cache

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

    def used_disk(self, path=None, unit='bytes'):
        """ Used disk on partition. Default location is cache folder.
        """
        if path is None:
            path = self._cache.cache

        return self.total_disk(path, unit) - self.available_disk(path, unit)

    def total_disk(self, path=None, unit='bytes'):
        """ Total disk on partition. Default location is cache folder.
        """
        if path is None:
            path = self._cache.cache

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

    def disk_ready(self, path=None, ready_ratio=90.0):
        """ Checks the status of the disk. Basically if there is enough space
            left. The default location is cache dir.
        """
        if path is None:
            path = self._cache.cache

        disk_ratio = ( float(self.used_disk(path)) / \
                           float(self.total_disk(path)) * 100
                       )

        return disk_ratio < ready_ratio, disk_ratio

    def set_usage(self, mode=None, expiration=1.0):
        """ Customize cache usage.

            Parameters
            ----------
            mode: string
                'online' or 'offline':
                    - online will always query the server to have up
                      to date data.
                    - offline will only try to query the server if the
                      data is not cached.
            expiration: float
                Relevant only to online mode. The cache has an
                expiration mechanism. If two queries on the same
                resource are issued under the specified value, the
                cache will be used and the server will not be
                requested.
        """
        if mode == 'online':
            self._intf._mode = 'online'
            self._intf._memtimeout = expiration
        elif mode == 'offline':
            self._intf._mode = 'offline'
            self._intf._memtimeout = expiration
        else:
            self._intf._memtimeout = expiration
