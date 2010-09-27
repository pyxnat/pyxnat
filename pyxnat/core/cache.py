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
from fnmatch import fnmatch
from StringIO import StringIO

from ..externals import simplejson as json
from ..externals import httplib2

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


class SQLCache(object):
    def __init__(self, cache, interface, safe=md5name):
        self.cache = cache
        self.safe = safe
        self._intf = interface

        self.computation_times = {}

        if not os.path.exists(cache): 
            os.makedirs(self.cache)

        self._db = sqlutil.init_db(os.path.join(self.cache, 'cache.db'), timeout=10.0)

#        self._db = sqlite3.connect(os.path.join(self.cache, 'cache.db'), 
#                                   timeout=10.0)
#                                   isolation_level='EXCLUSIVE')
        self._db.text_factory = str

        sqlutil.create_table(self._db, 'Http', 
                             [('uri', 'TEXT PRIMARY KEY'),
                              ('type', 'TEXT NOT NULL'),
                              ('size', 'INTEGER NOT NULL'),
                              ('computation_time', 'REAL NOT NULL'),
                              ('access_time', 'REAL NOT NULL'),
                              ('cost', 'REAL NOT NULL'),]
                             )

#        self._db.execute('CREATE TABLE IF NOT EXISTS Http '
#                         '('
#                         'uri TEXT PRIMARY KEY, type TEXT NOT NULL, '
#                         'size INTEGER NOT NULL, computation_time REAL NOT NULL, '
#                         'access_time REAL NOT NULL, cost REAL NOT NULL'
#                         ')'
#                         )

        sqlutil.create_table(self._db, 'Subjects',
                             [('subject_id', 'TEXT PRIMARY KEY'),
                              ('last_modified', 'TEXT NOT NULL'),]
                             )

#        self._db.execute('CREATE TABLE IF NOT EXISTS Subjects '
#                         '(subject_id TEXT PRIMARY KEY,'
#                         ' last_modified TEXT NOT NULL)'
#                         )

        sqlutil.create_table(self._db, 'Catalog',
                             [('location', 'TEXT PRIMARY KEY'),
                              ('uri', 'TEXT NOT NULL'),]
                             )

#        self._db.execute('PRAGMA temp_store=MEMORY')
#        self._db.execute('PRAGMA synchronous=OFF')
#        self._db.execute('PRAGMA cache_size=1048576')
#        self._db.execute('PRAGMA count_changes=OFF')

        self._db.commit()

    def set(self, key, value):
        cachepath = os.path.join(self.cache, self.safe(key))

        header = ''
        value = StringIO(value)

        while len(header) < 4 or header[-4:] != '\r\n\r\n':
            header += value.read(1)

        content = value.read()

        # headers extraction
        content_type = re.findall('(?<=content-type:\s).*?(?=\r\n|$)', header)[0]

        # compute size (at most 28 bytes are needed to store 2 int/long and 3 floats/doubles)
        size = len(content_type) + len(content) + len(header) + len(key) + 32

        space_left = self._intf.cache.space_left()
        if space_left < size:
            self._intf.cache.free_space(str(size - space_left)+'K')

        # get cache entry if it exists

#        entry = self._db.execute("SELECT * FROM Http WHERE uri=?", (key, )).fetchone()
        entry = sqlutil.get_one(self._db, 'Http', 'uri', key)

        if entry is None:
            access_time = self._intf._memcache.get(key, time.time())
            computation_time = self.computation_times.get(key, 1)
            delta_t = time.time() - access_time
            alpha = 1 - computation_time
            cost = alpha*size + size
            sqlutil.insert(self._db, 'Http', [key, content_type,
                                              size, computation_time, 
                                              access_time, cost]
                           )

#            self._db.execute("INSERT INTO Http VALUES (?, ?, ?, ?, ?, ?)",
#                             (key, content_type, size, computation_time, access_time, cost)
#                             )
        else:
            access_time = self._intf._memcache.get(key, entry[4])
            computation_time = self.computation_times.get(key, entry[3])

            delta_t = time.time() - access_time
            alpha = 1 - computation_time/delta_t
            last_cost = entry[5]
            cost = alpha*last_cost + size

            # larger is better
            sqlutil.update(self._db, 'Http', 
                           where_key='uri', 
                           dict_items={'type':content_type,
                                      'size':size,
                                      'computation_time':computation_time,
                                      'access_time':access_time,
                                      'cost':cost,
                                      'uri':key,
                                      }
                           )

#            self._db.execute("UPDATE Http "
#                             "SET type=?, size=?, computation_time=?, "
#                             "access_time=?, cost=? "
#                             "WHERE uri=?",
#                             (content_type, size, computation_time, access_time, cost, key)
#                             )

        f = file(cachepath+'.headers', "wb")
        f.write(header)
        f.close()

        f = file(cachepath, "wb")
        f.write(content)
        f.close()
    
        self._db.commit()

        if DEBUG:
            print key
            print 'computation_time: %s'%computation_time
            print 'access_time: %s'%access_time
            print 'size: %s'%size
            print 'cost: %s'%cost

    def put_in_catalog(self, key, alternative_cachepath, delete_original=False):
        sqlutil.insert_or_update(self._db, 'Catalog', 'location', 
                                 [('location', alternative_cachepath),
                                  ('uri', key)
                                  ], 
                                 commit=True
                                )

        original_path = os.path.join(self.cache, self.safe(key))

        if self.basepath(key) != alternative_cachepath:
            shutil.copy2(self.basepath(key), alternative_cachepath)

        if delete_original and os.path.exists(original_path):
            os.remove(original_path)
            # update size to 0 or header size in Http Table
            # add a size column to the catalog?

    def get(self, key):
        retval = None
        cachepath = os.path.join(self.cache, self.safe(key))

        try:
            f = file(cachepath+'.headers', "rb")
            retval = f.read()
            f.close()
        except IOError:
            return retval

        try:
            f = file(cachepath, "rb")
            retval += f.read()
            f.close()
        except IOError:
            cachepath = self.basepath(key)

            if cachepath != '':
                f = file(cachepath, "rb")
                retval += f.read()
                f.close()
            else:
                retval = None

        return retval

    def basepath(self, key):
        cachepath = os.path.join(self.cache, self.safe(key))
        if os.path.exists(cachepath):
            return cachepath
        else:
            for path, in \
                self._db.execute('SELECT location FROM Catalog WHERE uri=?', 
                                                       (key, ) ).fetchall():
                if os.path.exists(path):
                    return path

        return ''

    def delete(self, key):
        cachepath = os.path.join(self.cache, self.safe(key))
        
        try:
            sqlutil.delete(self._db, 'Http', 'uri', key)
#            self._db.execute("DELETE FROM Http WHERE uri=?", (key, ))
        except Exception,e :
#            print e
#            self._db = sqlite3.connect(os.path.join(self.cache, 'cache.db'), 
#                                       timeout=10.0)
            self._db = sqlutil.init_db(os.path.join(self.cache, 'cache.db'), timeout=10.0)
            return self.delete(key)

        if os.path.exists(cachepath+'.headers'):
            os.remove(cachepath+'.headers')

        if os.path.exists(cachepath):
            os.remove(cachepath)

        self._db.commit()


class CacheManager(object):
    def __init__(self, interface):
        self._intf = interface
        self._db = self._intf._conn.cache._db
        self.size_limit = None
        self.prioritize = ''

    def clear(self):
        [os.remove(entry) for entry in glob.iglob(os.path.join(self._intf._cachedir, '*'))]
        self._intf._connect()
        self._db = self._intf._conn.cache._db

    def free_space(self, size='1M'):
        size = memstr_to_bytes(size)
        freed = 0

        if 'files' in self.prioritize:
            dispensable = ("SELECT uri, size FROM Http "
                           "WHERE type<>'application/octet-stream' "
                           "ORDER BY cost ASC"
                           )
        elif 'resources' in self.prioritize:
            dispensable = ("SELECT uri, size FROM Http "
                           "WHERE type='application/octet-stream' "
                           "ORDER BY cost ASC"
                           )
        else:
            dispensable = "SELECT uri, size FROM Http ORDER BY cost ASC"

        for uri, entry_size in self._db.execute(dispensable).fetchall():
            if DEBUG:
                print 'free: %s %s'%(entry_size, uri)
            self._intf._conn.cache.delete(uri)
            freed += entry_size

            if freed >= size:
                break

    def space_left(self):
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
            return self.size_limit - self.space_used()

    def space_used(self):
        used = 0

        for size in self._db.execute("SELECT size FROM Http").fetchall():
            used += size[0]

        used += os.path.getsize(os.path.join(self._intf._cachedir, 'cache.db'))

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

    def set_strategy(self, size_limit='1G', prioritize=None):
        self.size_limit = memstr_to_bytes(size_limit)
        self.prioritize = prioritize or self.prioritize

    def diff(self):
        url = join_uri(self._intf._server, '/REST/subjects?format=csv&columns=ID,last_modified')

        content = self._intf._exec('/REST/subjects?format=csv&columns=ID,last_modified')
        server_version = JsonTable(csv_to_json(content)).select(['ID', 'last_modified'])
        server_version.order_by = ['ID', 'last_modified']

        return [diff[0] \
                for diff in set(self._db.execute("SELECT subject_id, last_modified from Subjects").fetchall()
                               ).symmetric_difference(server_version.items())
                ]
        
    def sync(self, data='all'):
        url = join_uri(self._intf._server, '/REST/subjects?format=csv&columns=ID,last_modified')

        content = self._intf._exec('/REST/subjects?format=csv&columns=ID,last_modified')
        server_version = JsonTable(csv_to_json(content)).select(['ID', 'last_modified'])
        server_version.order_by = ['ID', 'last_modified']

        not_diff = set(self._db.execute("SELECT subject_id, last_modified from Subjects").fetchall()
                      ).intersection(server_version.items())

        if 'files' in data:
            to_sync = ("SELECT uri FROM Http "
                       "WHERE type='application/octet-stream'"
                       )
        elif 'resources' in data:
            to_sync = ("SELECT uri FROM Http "
                       "WHERE type<>'application/octet-stream' "
                       )
        else:
            to_sync = "SELECT uri FROM Http"

        for entry in self._db.execute(to_sync).fetchall():
            if not any(subject[0] in entry[0] for subject in not_diff):    
                self._intf._exec(re.findall('/REST/.*', entry[0])[0])

        for subject in server_version:
            subject_id = subject['ID']
            last_modified = subject['last_modified']

            entry = self._db.execute("SELECT 1 FROM Subjects WHERE subject_id=?", (subject_id, )).fetchone()

            if entry is None:
                self._db.execute("INSERT INTO Subjects VALUES (?, ?)", (subject_id, last_modified))
            else:
                self._db.execute("UPDATE Subjects SET last_modified=? WHERE subject_id=?",
                                 (last_modified, subject_id))

        self._db.commit()

    def get(self, uri, column):
        return self._db.execute("SELECT %s FROM Http WHERE uri=?"%column, (uri, )).fetchone()[0]

    def entries(self):
        return [uri[0] for uri in self._db.execute("SELECT uri FROM Http")]

    def recover(self):
        if os.path.exists(os.path.join(self._intf._cachedir, 'cache.db')):
            os.remove(os.path.join(self._intf._cachedir, 'cache.db'))
        if os.path.exists(os.path.join(self._intf._cachedir, 'cache.db-journal')):
            os.remove(os.path.join(self._intf._cachedir, 'cache.db-journal'))

        self._intf._connect()
        self._db = self._intf._conn.cache._db

        # repopulate Http table from files
        for header_path in glob.iglob(os.path.join(self._intf._cachedir, '*.headers')):
            fd = open(header_path, 'rb')
            header = fd.read()
            fd.close()

            # extract headers info
            message = email.message_from_string(header)
            content_type = message.get('content-type')
            key = message.get('content-location')

            # compute entry size
            header_size = os.path.getsize(header_path)
            content_size = os.path.getsize(header_path.split('.header')[0])
            entry_size = len(content_type) + len(key) + 32

            size = header_size + content_size + entry_size

            access_time = time.time()
            computation_time = 1
            delta_t = time.time() - access_time
            alpha = 1 - computation_time
            cost = alpha*size + size

            self._db.execute("INSERT INTO Http VALUES (?, ?, ?, ?, ?, ?)",
                             (key, content_type, size, computation_time, access_time, cost)
                             )

        # repopulate Subjects table from file if exists
        subjects_table_uri = '/REST/subjects?format=csv&columns=ID,last_modified'
        subjects_table_path = os.path.join(self._intf._cachedir, 
                                           md5name(join_uri(self._intf._server, subjects_table_uri))
                                           )

        if os.path.exists(subjects_table_path):
            fd = open(subjects_table_path, 'rb')
            subjects_table = JsonTable(csv_to_json(fd.read())).select(['ID', 'last_modified'])
            fd.close()

            for subject in subjects_table:
                self._db.execute("INSERT INTO Subjects VALUES (?, ?)", 
                                    (subject['ID'], subject['last_modified']))

        self._db.commit()


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



