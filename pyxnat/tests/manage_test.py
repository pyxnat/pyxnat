from .. import Interface

central = Interface('https://central.xnat.org', 'nosetests', 'nosetests')

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

