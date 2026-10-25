"""Offline checks for saved credential-file permissions."""
import errno
import json
import os
import stat

import pytest

from pyxnat import Interface


@pytest.fixture
def interface():
    interface = Interface.__new__(Interface)
    interface._anonymous = False
    interface._server = 'https://example.invalid'
    interface._user = 'synthetic-user'
    interface._pwd = 'synthetic-password'
    interface._verify = None
    interface._proxy_url = None
    return interface


@pytest.mark.skipif(os.name != 'posix', reason='POSIX file permissions')
@pytest.mark.parametrize('existing', [False, True])
def test_save_config_restricts_permissions(tmp_path, existing, interface):
    path = tmp_path / 'credentials.json'

    previous_umask = os.umask(0o022)
    try:
        if existing:
            path.write_text('{}')
            path.chmod(0o644)
        interface.save_config(str(path))
    finally:
        os.umask(previous_umask)

    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert json.loads(path.read_text()) == {
        'server': 'https://example.invalid',
        'user': 'synthetic-user',
        'password': 'synthetic-password',
    }


@pytest.mark.skipif(os.name != 'posix', reason='POSIX file permissions')
def test_save_config_restricts_permissions_before_fdopen(tmp_path, monkeypatch,
                                                       interface):
    path = tmp_path / 'credentials.json'
    path.write_text('{}')
    path.chmod(0o644)
    fdopen = os.fdopen
    modes = []

    def record_mode(fd, *args, **kwargs):
        modes.append(stat.S_IMODE(os.fstat(fd).st_mode))
        return fdopen(fd, *args, **kwargs)

    monkeypatch.setattr(os, 'fdopen', record_mode)
    interface.save_config(str(path))
    assert modes == [0o600]


@pytest.mark.parametrize('operation', [
    pytest.param('fchmod', marks=pytest.mark.skipif(
        os.name != 'posix', reason='POSIX file permissions')),
    'fdopen',
])
def test_save_config_closes_descriptor_on_setup_error(tmp_path, monkeypatch,
                                                     interface, operation):
    descriptors = []
    error = OSError('config setup failed')

    def fail(fd, *args, **kwargs):
        descriptors.append(fd)
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(os, operation, fail)
        with pytest.raises(OSError) as caught:
            interface.save_config(str(tmp_path / 'credentials.json'))
    assert caught.value is error
    try:
        with pytest.raises(OSError) as closed:
            os.fstat(descriptors[0])
        assert closed.value.errno == errno.EBADF
    finally:
        try:
            os.close(descriptors[0])
        except OSError as exc:
            assert exc.errno == errno.EBADF


def test_save_config_closes_file_on_json_error(tmp_path, monkeypatch, interface):
    streams = []
    error = ValueError('cannot encode config')

    def fail(config, stream):
        streams.append((stream, stream.fileno()))
        raise error

    monkeypatch.setattr(json, 'dump', fail)
    with pytest.raises(ValueError) as caught:
        interface.save_config(str(tmp_path / 'credentials.json'))
    assert caught.value is error
    assert streams[0][0].closed
    with pytest.raises(OSError) as closed:
        os.fstat(streams[0][1])
    assert closed.value.errno == errno.EBADF
