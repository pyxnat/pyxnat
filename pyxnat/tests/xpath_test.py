import os.path as op
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

central = Interface('https://www.nitrc.org/ir', anonymous=True)


@skip_if_no_network
def test_001_xpath_checkout():
    central.xpath.checkout(subjects=['xnat_S02582', 'xnat_S02583'])
    assert 'xnat_S02582' in central.xpath.subjects() and \
        'xnat_S02583' in central.xpath.subjects()


@skip_if_no_network
def test_elements():
    assert 'xnat:voxelRes' in central.xpath.elements()


@skip_if_no_network
def test_keys():
    assert 'ID' in central.xpath.keys()


@skip_if_no_network
def test_values():
    assert 'xnat_S02582' in central.xpath.values('ID')


@skip_if_no_network
def test_element_attrs():
    assert isinstance(central.xpath.element_attrs('xnat:voxelRes'), list)
    assert {'x', 'y', 'z'}.issubset(central.xpath.element_keys('xnat:voxelRes'))
    assert '0.9375' in central.xpath.element_values('xnat:voxelRes', 'x')
