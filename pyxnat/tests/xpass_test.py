from pyxnat import xpass


def test_find_plus_line():
    print("Testing find_plus_line")
    test = ['hello', '+hello world', '']
    assert(xpass.find_plus_line(test) == 'hello world')
    test2 = ['', 'hello world']
    assert(xpass.find_plus_line(test2) is None)
    test3 = []
    assert(xpass.find_plus_line(test3) is None)


def test_find_token():
    print("Testing find_token")
    str = "hello,world"
    assert(xpass.find_token(',', str) == ('hello', 'world'))
    assert(xpass.find_token(' ', str) is None)


def test_parse_xnat_pass():
    print("Testing parse_xnat_pass")
    nothingLine = ""
    line = "+user@localhost:8080/xnat=password"
    lineWithSpaces = "+user@localhost:8080/xnat=password     "
    lineWithoutPlus = "user@localhost:8080/xnat=password"
    lineWithoutUser = "+@localhost:8080/xnat=password"
    lineWithoutHost = "+user=password"
    lineWithoutPass = "+user@localhost:8080/xnat"
    xp = xpass.parse_xnat_pass([nothingLine, line])
    assert(xp == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    xp = xpass.parse_xnat_pass([lineWithSpaces])
    assert(xp == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert(xpass.parse_xnat_pass([lineWithoutPlus]) is None)
    assert(xpass.parse_xnat_pass([lineWithoutUser]) is None)
    assert(xpass.parse_xnat_pass([lineWithoutHost]) is None)
    assert(xpass.parse_xnat_pass([lineWithoutPass]) is None)
