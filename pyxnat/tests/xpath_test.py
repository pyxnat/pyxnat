import os.path as op
from pyxnat import Interface
from . import skip_if_no_network

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)


@skip_if_no_network
def test_001_xpath_checkout():
    central.xpath.checkout(subjects=['OAS1_0001', 'OAS1_0002'])
    assert 'OAS1_0001' in central.xpath.subjects() and \
        'OAS1_0002' in central.xpath.subjects()


@skip_if_no_network
def test_elements():
    assert 'fs:region' in central.xpath.elements()


@skip_if_no_network
def test_keys():
    assert 'ID' in central.xpath.keys()


@skip_if_no_network
def test_values():
    assert 'OAS1_0002' in central.xpath.values('ID')


@skip_if_no_network
def test_element_attrs():
    assert isinstance(central.xpath.element_attrs('fs:region'), list)

    assert set(['SegId', 'hemisphere', 'name']).issubset(
        central.xpath.element_keys('fs:region'))

    assert 'Left-Putamen' in \
        central.xpath.element_values('fs:region', 'name')
