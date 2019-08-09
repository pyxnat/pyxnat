import os.path as op
from .. import Interface
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_xpath_checkout():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    central.xpath.checkout(subjects=['OAS1_0001', 'OAS1_0002'])
    assert 'OAS1_0001' in central.xpath.subjects() and \
        'OAS1_0002' in central.xpath.subjects()

def test_elements():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'fs:region' in central.xpath.elements()

def test_keys():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'ID' in central.xpath.keys()

def test_values():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert 'OAS1_0002' in central.xpath.values('ID')

def test_element_attrs():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    assert isinstance(central.xpath.element_attrs('fs:region'), list)

    assert set(['SegId', 'hemisphere', 'name']).issubset(
        central.xpath.element_keys('fs:region'))

    assert 'Left-Putamen' in \
        central.xpath.element_values('fs:region', 'name')
