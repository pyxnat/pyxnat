from .. import xpass

def test_find_plus_line():
    print "Testing find_plus_line"
    test = ['hello', '+hello world', '']
    assert(xpass.find_plus_line(test) == 'hello world')
    test2 = ['','hello world']
    assert(xpass.find_plus_line(test2) == None)
    test3 = []
    assert(xpass.find_plus_line(test3) == None)

def test_find_token():
    print "Testing find_token"
    str = "hello,world"
    assert(xpass.find_token(',',str) == ('hello','world'))
    assert(xpass.find_token(' ',str) == None)

def test_parse_xnat_pass():
    print "Testing parse_xnat_pass"
    nothingLine = ""
    line = "+user@localhost:8080/xnat=password"
    lineWithSpaces="+user@localhost:8080/xnat=password     "
    lineWithoutPlus = "user@localhost:8080/xnat=password"
    lineWithoutUser = "+@localhost:8080/xnat=password"
    lineWithoutHost = "+user=password"
    lineWithoutPass = "+user@localhost:8080/xnat"
    assert(xpass.parse_xnat_pass([nothingLine,line]) == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert(xpass.parse_xnat_pass([lineWithSpaces]) == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert(xpass.parse_xnat_pass([lineWithoutPlus]) == None)
    assert(xpass.parse_xnat_pass([lineWithoutUser]) == None)
    assert(xpass.parse_xnat_pass([lineWithoutHost]) == None)
    assert(xpass.parse_xnat_pass([lineWithoutPass]) == None)

