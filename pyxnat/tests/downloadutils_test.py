from .. import Interface
from pyxnat.core import downloadutils as du
import os.path as op
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_download():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    e = central.select.project('CENTRAL_OASIS_LONG').subject('OAS2_0001').experiment('CENTRAL_E00090')
    du.download(dest_dir='/tmp', instance=e.scans(), extract=True, removeZip=True)
