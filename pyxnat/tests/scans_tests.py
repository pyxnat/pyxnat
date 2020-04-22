from pyxnat import Interface
import os.path as op
from . import skip_if_no_network
from nose import SkipTest

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

@skip_if_no_network
def test_global_scan_listing():
    assert central.array.scans(project_id='CENTRAL_OASIS_CS',
                               experiment_type='xnat:mrSessionData',
                               scan_type='xnat:mrScanData'
                               )
