import os
from .. import Interface
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest
central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))

notified = []

def notify(cobj, eobj):
    notified.append(eobj)

def test_register_callback():
    local_notified = []
    central.manage.register_callback(notify)
    for element in central.select('/projects'):
        local_notified.append(element)

    assert notified == local_notified

def test_unregister_callback():
    central.manage.unregister_callback()
    assert central._callback is None

def test_add_schema():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert(len(central.manage.schemas()) == 0)
    central.manage.schemas.add(url='/xapi/schemas/xnat')
    assert(list(central.manage.schemas()) == ['xnat'])
