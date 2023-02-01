from pyxnat import Interface
import os.path as op
from pyxnat.tests import skip_if_no_network

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)


@skip_if_no_network
def test_prearchive_get():
    from pyxnat.core import manage
    pa = manage.PreArchive(central)
    pa.get()


@skip_if_no_network
def test_prearchive_status():
    triple = ['SAFMD', '20170602_161757472', '_4']
    from pyxnat.core import manage
    pa = manage.PreArchive(central)
    assert(pa.status(triple) == 'READY')
    pa.get_uri(triple)
