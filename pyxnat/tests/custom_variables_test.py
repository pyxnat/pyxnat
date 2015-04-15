import os
from uuid import uuid1

from .. import Interface

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))
project = central.select('/project/nosetests')

variables = {'Subjects' : {'newgroup' : {'foo' : 'string', 'bar' : 'int'}}}

sid = uuid1().hex
eid = uuid1().hex
cid = uuid1().hex

scan = project.subject(sid).experiment(eid).scan(cid).insert(use_label=True)

# def test_add_custom_variables():
#     project.add_custom_variables(variables)

# def test_get_custom_variables():
#     assert project.get_custom_variables() == variables

def test_set_param():
    
    scan.set_param('foo', 'foostring')
    scan.set_param('bar', '1')

    assert scan.params() == ['foo', 'bar']
    
def test_get_params():
    assert scan.get_params() == ['foostring', '1']

def test_params_cleanup():
    project.subject(sid).delete()
    assert not project.subject(sid).exists()
