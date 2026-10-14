"""Offline checks for saved credential-file permissions."""
import json
import os
import stat

import pytest

from pyxnat import Interface


@pytest.mark.skipif(os.name != 'posix', reason='POSIX file permissions')
@pytest.mark.parametrize('existing', [False, True])
def test_save_config_restricts_permissions(tmp_path, existing):
    interface = Interface.__new__(Interface)
    interface._anonymous = False
    interface._server = 'https://example.invalid'
    interface._user = 'synthetic-user'
    interface._pwd = 'synthetic-password'
    interface._verify = None
    interface._proxy_url = None
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
