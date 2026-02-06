from pyxnat import xpass


def test_find_plus_line():
    print("Testing find_plus_line")
    test = ['hello', '+hello world', '']
    assert (xpass.find_plus_line(test) == 'hello world')
    test2 = ['', 'hello world']
    assert (xpass.find_plus_line(test2) is None)
    test3 = []
    assert (xpass.find_plus_line(test3) is None)


def test_find_token():
    print("Testing find_token")
    string = "hello,world"
    assert (xpass.find_token(',', string) == ('hello', 'world'))
    assert (xpass.find_token(' ', string) is None)


def test_parse_xnat_pass():
    print("Testing parse_xnat_pass")
    nothing_line = ""
    line = "+user@localhost:8080/xnat=password"
    line_with_spaces = "+user@localhost:8080/xnat=password     "
    line_without_plus = "user@localhost:8080/xnat=password"
    line_without_user = "+@localhost:8080/xnat=password"
    line_without_host = "+user=password"
    line_without_pass = "+user@localhost:8080/xnat"
    xp = xpass.parse_xnat_pass([nothing_line, line])
    assert (xp == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    xp = xpass.parse_xnat_pass([line_with_spaces])
    assert (xp == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert (xpass.parse_xnat_pass([line_without_plus]) is None)
    assert (xpass.parse_xnat_pass([line_without_user]) is None)
    assert (xpass.parse_xnat_pass([line_without_host]) is None)
    assert (xpass.parse_xnat_pass([line_without_pass]) is None)
