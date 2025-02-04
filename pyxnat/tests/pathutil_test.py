def test_pathutil_find_files():
    from pyxnat.core import pathutil
    res = pathutil.find_files('.')
    print(res)
