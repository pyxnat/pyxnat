import os
import tempfile

from .. import jsonutil

_csv_example = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                            'results.csv')

_list_of_dirs = jsonutil.csv_to_json(open(_csv_example, 'rb').read())

jtable = jsonutil.JsonTable(_list_of_dirs)

# coverage_tests
def test_dump_methods():
    jtable.dumps_csv()
    jtable.dumps_json()

    jtable.dump_csv(tempfile.mkstemp()[1])
    jtable.dump_json(tempfile.mkstemp()[1])

    jtable.where(psytool_audit_parentdata_audit9='0', 
                 psytool_audit_parentdata_audit2='0', 
                 psytool_audit_parentdata_audit1='2', 
                 psytool_audit_parentdata_audit10='2')

    jtable.where('5154')

    assert True

# unit_tests
def test_get_item_str_value():
    assert jtable['subject_label'] == jtable.get('subject_label')

def test_get_item_int_value():
    assert jtable.data[0] == jtable[0].data[0]

def test_get_item_list_value():
    assert set(jtable[['projects', 'subjectid']].headers()) == set(['projects', 'subjectid'])

def test_join():
    index = jtable.headers().index('subjectid')
    a = jtable.select(jtable.headers()[:index+1])
    b = jtable.select(jtable.headers()[index:])
    c = a.join('subjectid', b)
    assert len(jtable.headers()) == len(c.headers())




