import os
from uuid import uuid1
from pyxnat import Interface
import os.path as op
from pyxnat.tests import skip_if_no_network


fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)
project = central.select.project('pyxnat_tests')

variables = {'Subjects': {'newgroup': {'foo': 'string', 'bar': 'int'}}}

sid = uuid1().hex
eid = uuid1().hex
cid = uuid1().hex

if not os.environ.get('PYXNAT_SKIP_NETWORK_TESTS'):
    sc = project.subject(sid).experiment(eid).scan(cid)
    scan = sc.insert(use_label=True)


@skip_if_no_network
def test_01_set_param():
    scan.set_param('foo', 'foostring')
    scan.set_param('bar', '1')

    assert scan.params() == ['foo', 'bar']


@skip_if_no_network
def test_02_get_params():
    assert scan.get_params() == ['foostring', '1']


@skip_if_no_network
def test_03_params_cleanup():
    project.subject(sid).delete()
    assert not project.subject(sid).exists()


@skip_if_no_network
def test_04_add_custom_variables():
    project.add_custom_variables(variables)


@skip_if_no_network
def test_05_get_custom_variables():
    project.get_custom_variables()
