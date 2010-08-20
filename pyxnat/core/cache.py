import os
import platform
import ctypes
import glob
import hashlib
import re
import sqlite3
import time
from fnmatch import fnmatch
from StringIO import StringIO

from ..externals import simplejson as json
from ..externals import httplib2

_platform = platform.system()

DEBUG = False

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
        self.durations = {}

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

class SQLCache(object):
    def __init__(self, cache, interface, safe=md5name):
        self.cache = cache
        self.safe = safe
        self._intf = interface

        self.durations = {}

        if not os.path.exists(cache): 
            os.makedirs(self.cache)

        self._db = sqlite3.connect(os.path.join(self.cache, 'cache.db'))
        self._db.text_factory = str
        self._db.execute('CREATE TABLE IF NOT EXISTS http '
                         '('
                         'uri TEXT PRIMARY KEY, content_size INTEGER NOT NULL, '
                         'content_type TEXT NOT NULL, content_location TEXT NOT NULL, '
                         'last_modified TEXT NOT NULL, last_duration REAL NOT NULL, '
                         'last_access REAL NOT NULL, access_nb INTEGER NOT NULL, '
                         'cost REAL NOT NULL'
                         ')'
                         )

        self._db.execute('PRAGMA temp_store=MEMORY')
        self._db.execute('PRAGMA synchronous=OFF')
        self._db.execute('PRAGMA cache_size=1048576')
        self._db.execute('PRAGMA count_changes=OFF')

        self._db.commit()

    def set(self, key, value):
        cachepath = os.path.join(self.cache, self.safe(key))

        header = ''
        value = StringIO(value)

        while len(header) < 4 or header[-4:] != '\r\n\r\n':
            header += value.read(1)

        content = value.read()

        f = file(cachepath+'.headers', "wb")
        f.write(header)
        f.close()

        f = file(cachepath, "wb")
        f.write(content)
        f.close()

        content_size = len(content)
        
        # headers extraction
        last_modified = re.findall('(?<=last-modified:\s).*?(?=\r\n|$)', header)
        last_modified = '' if last_modified == [] else last_modified[0]
        content_type = re.findall('(?<=content-type:\s).*?(?=\r\n|$)', header)[0]
        content_location = re.findall('content-location:\shttp.?://.*?(?=\r\n|$)', header)
        content_location = '' if content_location == [] \
                              else content_location[0].split('/REST')[1].split('?')[0]

        # index values
        entry = self._db.execute("SELECT * FROM http WHERE uri=?", (key, )).fetchone()

        if self._intf.cache.size_limit is not None:
            if self._intf.cache.size_limit < self._intf.cache.used_space():
                self._intf.cache.free(self._intf.cache.used_space() - \
                                        self._intf.cache.size_limit + \
                                            content_size)

        elif self._intf.cache.free_space() < content_size:
            self._intf.cache.free(content_size)

        if entry is None:
            access_nb = 1
            last_access = self._intf._memcache.get(key, time.time())
            last_duration = self.durations.get(key, 1)
            cost = (last_duration*content_size*access_nb*last_access)/(time.time())

            self._db.execute("INSERT INTO http VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (key, content_size, content_type, content_location,
                              last_modified, last_duration, last_access, access_nb, cost)
                             )
        else:
            access_nb = entry[7] + 1
            last_access = self._intf._memcache.get(key, entry[6])
            last_duration = self.durations.get(key, entry[5])

            cost = (last_duration*content_size*entry[5]*entry[6])/(time.time())

            self._db.execute("UPDATE http "
                             "SET content_size=?, content_type=?, content_location=?, "
                             "last_modified=?, last_duration=?, last_access=?, access_nb=?, cost=? "
                             "WHERE uri=?",
                             (content_size, content_type, content_location,
                              last_modified, last_duration, last_access, access_nb, cost, key)
                             )
    
        self._db.commit()

        if DEBUG:
            print key
            print 'last_duration: %s'%last_duration
            print 'last_access: %s'%last_access
            print 'access_nb: %s'%access_nb
            print 'size: %s'%content_size
            print 'cost: %s'%cost

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

    def delete(self, key):
        cachepath = os.path.join(self.cache, self.safe(key))
        
        self._db.execute("DELETE FROM http WHERE uri=?", (key, ))

        if os.path.exists(cachepath+'.headers'):
            os.remove(cachepath+'.headers')

        if os.path.exists(cachepath):
            os.remove(cachepath)

        self._db.commit()

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


class NewCacheManager(object):
    def __init__(self, interface):
        self._intf = interface
        self._db = self._intf._conn.cache._db
        self.size_limit = None
        self.prioritize = None

    def clear(self):
        [os.remove(entry) for entry in glob.iglob(os.path.join(self._intf._cachedir, '*'))]

    def free(self, size=0):
        freed = 0

        if 'files' in self.prioritize:
            dispensable = ("SELECT uri, content_size FROM http "
                           "WHERE content_type<>'application/octet-stream' "
                           "ORDER BY cost ASC"
                           )
        elif 'resources' in self.prioritize:
            dispensable = ("SELECT uri, content_size FROM http "
                           "WHERE content_type='application/octet-stream' "
                           "ORDER BY cost ASC"
                           )
        else:
            dispensable = "SELECT uri, content_size FROM http ORDER BY cost ASC"

        for uri, content_size in self._db.execute(dispensable):
            if DEBUG:
                print 'free: %s %s'%(content_size, uri)
            self._intf._conn.cache.delete(uri)
            freed += content_size

            if freed >= size:
                break

    def free_space(self):

        if self.size_limit is None:
            if _platform == 'Windows':
                available = ctypes.c_ulonglong(0)

                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                                        ctypes.c_wchar_p(self._intf._cachedir),
                                        None, 
                                        None, 
                                        ctypes.pointer(available))

                return available.value
            else:
                cache_st = os.statvfs(self._intf._cachedir)

                return cache_st.f_bavail * cache_st.f_bsize
        else:
            return self.size_limit - self.used_space()

    def used_space(self):
        used = 0

        for content_size in self._db.execute("SELECT content_size FROM http"):
            used += content_size[0]

        used += os.path.getsize(os.path.join(self._intf._cachedir, 'cache.db'))

        return used

    def status(self):
        used_space = self.used_space()
        used_space_norm = float(used_space) / 10**6 if float(used_space) / 10**6 < 1000 \
                                                    else float(used_space) / 10**9
        used_space_unit = 'M' if float(used_space) / 10**6 < 1000 else 'G'

        free_space = self.free_space()
        free_space_norm = float(free_space) / 10**6 if float(free_space) / 10**6 < 1000 \
                                                    else float(free_space) / 10**9
        free_space_unit = 'M' if float(free_space) / 10**6 < 1000 else 'G'

        print 'used space: %s%s'%(round(used_space_norm, 2), used_space_unit)
        print 'free space: %s%s'%(round(free_space_norm, 2), free_space_unit)

    def set_strategy(self, size_limit=None, prioritize=None):
        self.size_limit = size_limit or self.size_limit
        self.prioritize = prioritize or self.prioritize

    def sync(self, data='all'):

#            find_subj = re.findall('(?<=/subjects/).*?(?=/|$)', uri)
#            if find_subj != []:
#                print 'find subj %s'%find_subj[0]
#                subj_uri = join_uri(self._server, 
#                                    '/REST/subjects?format=csv'
#                                    '&columns=ID,last_modified'
#                                    '&ID=%s'%find_subj[0]
#                                    )

#                r, c = self._conn.request(subj_uri, method, body, headers)
#                csv_to_json(c)[last_modified]
#                self.cache.


        if 'files' in data:
            to_sync = ("SELECT uri FROM http "
                       "WHERE content_type='application/octet-stream'"
                       )
        elif 'resources' in data:
            to_sync = ("SELECT uri FROM http "
                       "WHERE content_type<>'application/octet-stream' "
                       )
        else:
            to_sync = "SELECT uri FROM http"

        for entry in self._db.execute(to_sync):
            self._intf._exec(re.findall('/REST/.*', entry[0])[0])

    def get(self, uri, column):
        return self._db.execute("SELECT %s FROM http WHERE uri='uri'").fetchone()

    def entries(self):
        return [uri[0] for uri in self._db.execute("SELECT uri FROM http")]

    def reload(self):
        pass


