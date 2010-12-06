def all_experiments_xsiType(interface):

    for exp_type in interface.inspect.datatypes():
        try:
            out = interface._get_json('/REST/experiments?columns=ID,xsiType&xsiType=%s'%exp_type)
        except:
            continue

        yield exp_type

def all_subexp_xsiType(interface):
    for s in subexp_xsiType(interface, 0):
        yield s

def subexp_xsiType(interface, subexp, n=0, from_datatypes=[]):
    if from_datatypes == []:
        from_datatypes = all_experiments_xsiType(interface)

    for exp_type in from_datatypes:
        skip_type = False
        exp_list = '/REST/experiments?xsiType=%s'%exp_type

        for i, exp_res in enumerate(interface._get_json(exp_list)):
            if n!= 0 and i >= n:
                skip_type = True
                break
            try:
                subexp_list = ('/REST/experiments/%s'
                               '/%s?columns=ID,xsiType'%(subexp, exp_res['ID']))

                for subexp_res in interface._get_json(scan_list):
                    yield subexp_res

            except:
                print exp_type, 'does not have %s'%subexp
                skip_type = True
                break

        if skip_type:
            continue


#class GrabMe(object):
#    def __init__(self, interface):
#        self._intf = interface


#    def __call__(self, datatype)
