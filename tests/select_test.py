from pyxnat import select


def test_switch_to_singular():
    assert select.compute('/projects/nosetests') == ['/project/nosetests']

def test_switch_to_plural():
    assert select.compute('/project') == ['/projects/*']

def test_complete_stars_plural():
    assert select.compute('/projects/subjects/experiments') == ['/projects/*/subjects/*/experiments/*']

def test_complete_stars_singular():
    assert select.compute('/project/subject/experiment') == ['/projects/*/subjects/*/experiments/*']

def test_simple_root_expand():
    assert select.compute('//experiments') == ['/projects/*/subjects/*/experiments/*']

def test_simple_root_expand():
    assert select.compute('//experiments') == ['/projects/*/subjects/*/experiments/*']

def test_simple_level_expand():
    assert select.compute('/projects/IMAGEN//experiments') == ['/project/IMAGEN/subjects/*/experiments/*']

def test_leaf_level_expand():
    assert set(select.compute('//files')) == \
        set(['/projects/*/subjects/*/experiments/*/resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/reconstructions/*/in_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/scans/*/resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*',
             '/projects/*/subjects/*/resources/*/files/*',
             '/projects/*/resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/reconstructions/*/out_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*'])

def test_double_level_expand():
    assert set(select.compute('//experiments//files')) == \
        set(['/projects/*/subjects/*/experiments/*/resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/reconstructions/*/in_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/scans/*/resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/out_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/in_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/reconstructions/*/out_resources/*/files/*',
             '/projects/*/subjects/*/experiments/*/assessors/*/resources/*/files/*'])

def test_compute_all():
    assert set(select.compute('/projects/nosetests//experiments/*Session*//files/myfile.txt')) == \
        set(['/project/nosetests/subjects/*/experiments/*Session*/resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/reconstructions/*/in_resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/scans/*/resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/assessors/*/out_resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/assessors/*/in_resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/reconstructions/*/out_resources/*/file/myfile.txt',
             '/project/nosetests/subjects/*/experiments/*Session*/assessors/*/resources/*/file/myfile.txt'])
