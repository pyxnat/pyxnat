import os
import tempfile

from ..pyxnat import sqlutil


_loc = tempfile.mkstemp(suffix='.db')[1]

def test_init_db():
    assert sqlutil.init_db(_loc) is not None

def test_create_table():
    db = sqlutil.init_db(_loc)
    sqlutil.create_table(db, 'Test', [('key', 'TEXT PRIMARY KEY'), 
                                      ('int', 'INTEGER NOT NULL')],
                         commit=True
                         )

    assert 'Test' in sqlutil.db_tables(db)
    assert 'key' in sqlutil.table_columns(db, 'Test')
    assert 'int' in sqlutil.table_columns(db, 'Test')

def test_insert():
    db = sqlutil.init_db(_loc)
    sqlutil.insert(db, 'Test', ['one', 1], commit=True)

    results = dict(db.execute('SELECT key, int FROM Test').fetchall())
    assert results['one'] == 1

def test_update():
    db = sqlutil.init_db(_loc)

    sqlutil.update(db, 'Test', 'key', {'key':'one', 'int':2}, commit=True)

    results = dict(db.execute('SELECT key, int FROM Test').fetchall())
    assert results['one'] == 2

def test_insert_or_update():
    db = sqlutil.init_db(_loc)

    sqlutil.insert_or_update(db, 'Test', 'key', [('key', 'one'), ('int', 1)], commit=True)
    sqlutil.insert_or_update(db, 'Test', 'key', [('key', 'two'), ('int', 2)], commit=True)

    results = dict(db.execute('SELECT key, int FROM Test').fetchall())
    assert results['one'] == 1
    assert results['two'] == 2

def test_has_entry():
    db = sqlutil.init_db(_loc)

    assert sqlutil.has_entry(db, 'Test','key', 'one')
    assert not sqlutil.has_entry(db, 'Test','key', 'three')

def test_delete():
    db = sqlutil.init_db(_loc)

    assert sqlutil.has_entry(db, 'Test','key', 'two')
    sqlutil.delete(db, 'Test', 'key', 'two', commit=True)
    assert not sqlutil.has_entry(db, 'Test','key', 'two')

def cleanup():
    os.remove(_loc)
