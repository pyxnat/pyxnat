"""Offline tests for TLS configuration round-trips."""

import json

import pytest

from pyxnat import Interface


@pytest.mark.parametrize('verify', [True, False, '/custom CA/ca-bundle.pem'])
def test_config_preserves_tls_verification(tmp_path, verify):
    config_path = tmp_path / 'xnat.cfg'
    config_path.write_text(json.dumps({
        'server': 'https://xnat.example.invalid',
        'user': 'synthetic-user',
        'password': 'synthetic-password',
        'verify': verify,
    }))
    interface = Interface(config=str(config_path))
    try:
        assert interface._http.verify == verify
        saved_path = tmp_path / 'saved.cfg'
        interface.save_config(str(saved_path))
        assert json.loads(saved_path.read_text())['verify'] == verify
    finally:
        interface._http.close()


def test_config_defaults_to_certificate_verification(tmp_path):
    config_path = tmp_path / 'xnat.cfg'
    config_path.write_text(json.dumps({
        'server': 'https://xnat.example.invalid',
        'user': 'synthetic-user',
        'password': 'synthetic-password',
    }))
    interface = Interface(config=str(config_path))
    try:
        assert interface._http.verify is True
    finally:
        interface._http.close()
