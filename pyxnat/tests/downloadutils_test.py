from pyxnat import Interface
from pyxnat.core import downloadutils as du
import os.path as op
from . import skip_if_no_network

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

@skip_if_no_network
def test_download():
    e = central.select.project('CENTRAL_OASIS_LONG').subject('OAS2_0001').experiment('CENTRAL_E00090')
    du.download(dest_dir='/tmp', instance=e.scans(), extract=True, removeZip=True)
