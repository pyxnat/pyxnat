import os.path as op
import tempfile

from pyxnat import jsonutil

_csv_example = op.join(op.dirname(op.abspath(__file__)), 'results.csv')
_list_of_dirs = jsonutil.csv_to_json(open(_csv_example, 'r').read())

jtable = jsonutil.JsonTable(_list_of_dirs)


# coverage_tests
def test_dump_methods():
    jtable.__repr__()

    jtable.dumps_csv()
    jtable.dumps_json()

    jtable.dump_csv(tempfile.mkstemp()[1])
    jtable.dump_json(tempfile.mkstemp()[1])

    jtable.where(psytool_audit_parentdata_audit9='0',
                 psytool_audit_parentdata_audit2='0',
                 psytool_audit_parentdata_audit1='2',
                 psytool_audit_parentdata_audit10='2')

    jtable.where('5154')
    jtable.where_not('5154')

    assert True


# unit_tests
def test_get_item_str_value():
    jtable.items()
    assert jtable['subject_label'] == jtable.get('subject_label')


def test_get_item_int_value():
    assert jtable.data[0] == jtable[0].data[0]


def test_get_item_list_value():
    headers = set(jtable[['projects', 'subjectid']].headers())
    assert headers == set(['projects', 'subjectid'])


def test_join():
    index = list(jtable.headers()).index('subjectid')
    a = jtable.select(list(jtable.headers())[:index+1])
    b = jtable.select(list(jtable.headers())[index:])
    c = a.join('subjectid', b)
    assert len(list(jtable.headers())) == len(list(c.headers()))
