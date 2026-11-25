from pyxnat import Interface
import os.path as op
from pyxnat.tests import skip_if_no_network

fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)


@skip_if_no_network
def test_prearchive_get():
    from pyxnat.core import manage
    pa = manage.PreArchive(central)
    pa.get()


@skip_if_no_network
def test_prearchive_status():
    triple = ['pyxnat_tests', '20261125_145226882', 'sub_001_ses_01']
    from pyxnat.core import manage
    pa = manage.PreArchive(central)
    assert(pa.status(triple) == 'READY')
    pa.get_uri(triple)
