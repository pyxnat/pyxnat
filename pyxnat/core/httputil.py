
_boundary = '----------ThIs_Is_tHe_bouNdaRY_$'
_crlf = '\r\n'


def file_message(content, content_type, path, name):
    body = []
    body.append('--' + _boundary)
    body.append('Content-Disposition: form-data; '
                'name="%s"; filename="%s"' % (path, name)
                )
    body.append('Content-Type: %s' % content_type)
    body.append('')

    body.append(content)
    body.append('--' + _boundary + '--')
    body.append('')
    body = _crlf.join(body)
    content_type = 'multipart/form-data; boundary=%s' % _boundary

    return body, content_type
