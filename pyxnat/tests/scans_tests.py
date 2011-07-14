import os

from ..pyxnat import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface('http://sandbox.xnat.org/xnat', 'testuser', 'testuser')

def test_global_scan_listing():
    assert central.select.scans()
