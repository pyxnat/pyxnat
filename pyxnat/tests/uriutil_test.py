from .. import uriutil

def test_translate_uri():
    assert uriutil.translate_uri('/assessors/out_resources/files') == '/assessors/out/resources/files'
    assert uriutil.translate_uri('/assessors/out_resource/files') == '/assessors/out/resource/files'
    assert uriutil.translate_uri('/assessors/in_resources/files') == '/assessors/in/resources/files'
    assert uriutil.translate_uri('/assessors/in_resource/files') == '/assessors/in/resource/files'

def test_inv_translate_uri():
    assert uriutil.inv_translate_uri('/assessors/out/resources/files') == '/assessors/out_resources/files'
    assert uriutil.inv_translate_uri('/assessors/out/resource/files') == '/assessors/out_resource/files'
    assert uriutil.inv_translate_uri('/assessors/in/resources/files') == '/assessors/in_resources/files'
    assert uriutil.inv_translate_uri('/assessors/in/resource/files') == '/assessors/in_resource/files'

def test_join_uri():
    assert uriutil.join_uri('/projects', 'project_id', 'subjects', 'subject_id') == '/projects/project_id/subjects/subject_id'

def test_uri_last():
    assert uriutil.uri_last('/projects/1/subjects/2') == '2'

def test_uri_nextlast():
    assert uriutil.uri_nextlast('/projects/1/subjects/2') == 'subjects'

def test_uri_parent():
    assert uriutil.uri_parent('/projects/1/subjects/2') == '/projects/1/subjects'

def test_uri_grandparent():
    assert uriutil.uri_grandparent('/projects/1/subjects/2') == '/projects/1'

def test_uri_split():
    assert uriutil.uri_split('/projects/1/subjects/2') == ['/projects/1/subjects', '2']

