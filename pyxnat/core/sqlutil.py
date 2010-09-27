import sqlite3

def init_db(db_path, timeout=10.0, isolation_level=''):
    db = sqlite3.connect(db_path, timeout=timeout, isolation_level=isolation_level)

    db.execute('PRAGMA temp_store=MEMORY')
    db.execute('PRAGMA synchronous=OFF')
    db.execute('PRAGMA cache_size=1048576')
    db.execute('PRAGMA count_changes=OFF')    

    db.commit()
    
    return db

def create_table(db, name, cols=[], commit=False):
    db.execute('CREATE TABLE IF NOT EXISTS %s '
               '(%s)'%(name, ','.join(['%s %s'%(col[0], col[1]) for col in cols]))
              )

    if commit:
        db.commit()

def insert_or_update(db, table, where_key, list_items=[], commit=False):
    where_value = dict(list_items)[where_key]

    if not has_entry(db, table, where_key, where_value):
        insert(db, table, [item[1] for item in list_items], commit)
    else:
        update(db, table, where_key, dict(list_items), commit)
    
def has_entry(db, table, where_key, where_value):
    return db.execute("SELECT * FROM %s WHERE %s=?"%(table, where_key), 
                      (where_value, )
                      ).fetchone() is not None

def get_one(db, table, where_key, where_value):
    return db.execute("SELECT * FROM %s WHERE %s=?"%(table, where_key), 
                      (where_value, )
                      ).fetchone()

def get_all(db, table, where_key, where_value):
    return db.execute("SELECT * FROM %s WHERE %s=?"%(table, where_key), 
                      (where_value, )
                      ).fetchall()

def insert(db, table, values=[], commit=False):
    db.execute("INSERT INTO %s VALUES (%s)"%
                    (table, ', '.join(['?']*len(values))), tuple(values)
               )

    if commit:
        db.commit()

def update(db, table, where_key, dict_items={}, commit=False):
    where_value = dict_items.pop(where_key)

    db.execute("UPDATE %s SET %s WHERE %s=?"%
               (table,
                ', '.join(['%s=?'%col for col in dict_items.keys()]), 
                where_key
                ),
               tuple(dict_items.values()) + (where_value, )
               )

    if commit:
        db.commit()

def delete(db, table, where_key, where_value, commit=False):
    db.execute('DELETE FROM %s WHERE %s=?'%(table, where_key), 
               (where_value, ) 
               )

    if commit:
        db.commit()

def db_tables(db):
    return [table[1] for table in db.execute('SELECT * FROM sqlite_master')]

def table_columns(db, table):
    return [col[0] for col in db.execute('SELECT * FROM %s'%table).description]

