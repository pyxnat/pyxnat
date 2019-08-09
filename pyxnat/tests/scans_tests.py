from .. import Interface
import os.path as op
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest

_modulepath = op.dirname(op.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_global_scan_listing():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert central.array.scans(project_id='CENTRAL_OASIS_CS',
                               experiment_type='xnat:mrSessionData',
                               scan_type='xnat:mrScanData'
                               )
