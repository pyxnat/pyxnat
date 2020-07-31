import os.path as op
from pyxnat import Interface
from . import skip_if_no_network


fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)

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


@skip_if_no_network
def test_add_schema():
    assert(len(central.manage.schemas()) == 0)
    central.manage.schemas.add(url='/xapi/schemas/xnat')
    assert(list(central.manage.schemas()) == ['xnat'])
