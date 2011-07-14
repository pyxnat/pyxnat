import os
import string
import Utils
from  import *

# default path to xnat pass file
def path():
    return os.getenv('USERPROFILE') or os.getenv('HOME') + "/.xnatPass"

# str ->  {'host': ..., 'u': ..., 'p': ..., 'port': ...} | None
def readXnatPass(f):
    if os.path.exists(f) and os.path.isfile(f):
        infile = open(f)
        return parseXnatPass(infile.readlines())
    else:
        # raise IOError('XNAT Pass file :' + f + " does not exist")
        return None

# [str] -> {'host': ..., 'u': ..., 'p': ..., 'port':...} | None
def parseXnatPass(lines):
    empty = {'host': None,  'u': None, 'p': None}
    line = findPlusLine(lines)
    u = ('u',partial(findToken,'@'),True)
    host = ('host',partial(findToken,'='),True)
    p = ('p',partial(lambda x : (x,x)),True)
    
    def updateState(x,k,state):
        state[k] = x
        return state
    if line == None:
        return None
    else:
        return chain([u,host,p],line,empty,updateState)

# [(str, str -> str, bool)] ->
#  str ->
#  dict
#  dict -> dict
#  dict | None
def chain(ops, initEnv, initState, updateStateF):
    env = initEnv
    state = initState
    for op in ops:
        (k,_op,mandatory) = op
        tmp = _op(env)
        if tmp == None:
            if mandatory:
                return None
        else:
            (v,rest) = tmp
            env = rest
            state = updateStateF(v,k,state)
    return state
        
# [str] -> str | None
def findPlusLine(lines):
    plusLines = filter (lambda x: x.startswith('+'), lines)
    if len(plusLines) == 0:
        return None
    else:
        return Utils.tail(plusLines[0])

# char -> str -> (str,str) | None
def findToken(tok,line):
    splitString = Utils.split(tok,line)
    if len(splitString) == 0 or len(splitString) == 1 or splitString[0] == '':
        return None
    else:
        return (splitString[0],splitString[1])

## Tests
def findPlusLineTest():
    print "Testing findPlusLine"
    test = ['hello', '+hello world', '']
    assert(findPlusLine(test) == 'hello world')
    test2 = ['','hello world']
    assert(findPlusLine(test2) == None)
    test3 = []
    assert(findPlusLine(test3) == None)

def findTokenTest():
    print "Testing findToken"
    str = "hello,world"
    assert(findToken(',',str) == ('hello','world'))
    assert(findToken(' ',str) == None)

def parseXnatPassTest():
    print "Testing parseXnatPass"
    nothingLine = ""
    line = "+user@localhost:8080/xnat=password"
    lineWithSpaces="+user@localhost:8080/xnat=password     "
    lineWithoutPlus = "user@localhost:8080/xnat=password"
    lineWithoutUser = "+@localhost:8080/xnat=password"
    lineWithoutHost = "+user=password"
    lineWithoutPass = "+user@localhost:8080/xnat"
    assert(parseXnatPass([nothingLine,line]) == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert(parseXnatPass([lineWithSpaces]) == {'p': 'password', 'host': 'localhost:8080/xnat', 'u': 'user'})
    assert(parseXnatPass([lineWithoutPlus]) == None)
    assert(parseXnatPass([lineWithoutUser]) == None)
    assert(parseXnatPass([lineWithoutHost]) == None)
    assert(parseXnatPass([lineWithoutPass]) == None)
           
def test():
    findPlusLineTest()
    findTokenTest()
    parseXnatPassTest()
