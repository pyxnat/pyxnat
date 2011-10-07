from .. import Interface

central = Interface('https://central.xnat.org', 'nosetests', 'nosetests')

def test_xpath_checkout():
    central.xpath.checkout(subjects=['OAS1_0001', 'OAS1_0002'])
    assert 'OAS1_0001' in central.xpath.subjects() and \
        'OAS1_0002' in central.xpath.subjects()

def test_elements():
    assert 'fs:region' in central.xpath.elements()

def test_keys():
    assert 'ID' in central.xpath.keys()

def test_values():
    assert 'OAS1_0002' in central.xpath.values('ID')

def test_element_attrs():
    assert isinstance(central.xpath.element_attrs('fs:region'), list)

    assert set(['SegId', 'hemisphere', 'name']).issubset(
        central.xpath.element_keys('fs:region'))

    assert 'Left-Putamen' in \
        central.xpath.element_values('fs:region', 'name')

