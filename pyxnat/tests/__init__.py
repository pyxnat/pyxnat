from functools import wraps
import pytest
import os


def skip_if_no_network(func=None):
    """Skip test completely in NONETWORK settings
    If not used as a decorator, and just a function, could be used at the module level
    """

    def check_and_raise():
        if os.environ.get('PYXNAT_SKIP_NETWORK_TESTS'):
            pytest.skip("Skipping since no network settings")

    if func:
        @wraps(func)
        def newfunc(*args, **kwargs):
            check_and_raise()
            return func(*args, **kwargs)
        return newfunc
    else:
        check_and_raise()
