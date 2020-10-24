
def test_setup_docker_xnat():
    import os
    import pyxnat

    x = pyxnat.Interface(config='.xnat.cfg')

    cmd = 'curl --cookie-jar /tmp/cookie --header "Content-Type: application/x-www-form-urlencoded" '\
        '--request POST '\
        '--data "username={user}&password={password}&login=&XNAT_CSRF=" '\
        'http://localhost/login'.format(user=x._user, password=x._pwd)
    print(cmd)
    os.system(cmd)

    cmd = 'curl --cookie /tmp/cookie --header "Content-Type: application/json" '\
        '--request POST '\
        '--data \'%s\' '\
        'http://localhost/xapi/siteConfig'

    cmd2 = cmd % '{"siteId": "XNAT", "siteUrl": "http://localhost", "adminEmail": "fake@fake.fake"}'
    print(cmd2)
    os.system(cmd2)

    cmd2 = cmd % '{"archivePath":"/data/xnat/archive","prearchivePath":"/data/xnat/prearchive","cachePath":"/data/xnat/cache","buildPath":"/data/xnat/build","ftpPath":"/data/xnat/ftp","pipelinePath":"/data/xnat/pipeline","inboxPath":"/data/xnat/inbox"}'
    print(cmd2)
    os.system(cmd2)

    cmd2 = cmd % '{"requireLogin":true,"userRegistration":false,"enableCsrfToken":true}'
    print(cmd2)
    os.system(cmd2)

    cmd2 = cmd % '{"initialized":true}'
    print(cmd2)
    os.system(cmd2)


    p = x.select.project('nosetests')
    p.create()
    for i in range(3, 10):
        p = x.select.project('nosetests%s' % i)
        p.create()

    uri = '/data/projects/nosetests'
    options = {'alias': 'nosetests2'}
    data = x.put(uri, params=options).text
