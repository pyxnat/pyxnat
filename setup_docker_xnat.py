
if __name__ == '__main__':
    import pyxnat

    x = pyxnat.Interface(config='.xnat.cfg')
    p = x.select.project('nosetests')
    p.create()
    for i in range(3, 10):
        p = x.select.project('nosetests%s' % i)
        p.create()

    uri = '/data/projects/nosetests'
    options = {'alias': 'nosetests2'}
    data = x.put(uri, params=options).text
