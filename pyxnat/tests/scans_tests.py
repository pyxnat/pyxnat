import os

from .. import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))

def test_global_scan_listing():
    assert central.array.scans(project_id='CENTRAL_OASIS_CS', 
                               experiment_type='xnat:mrSessionData', 
                               scan_type='xnat:mrScanData'
                               )

