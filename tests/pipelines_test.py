import os.path as op
from pyxnat import Interface
from . import skip_if_no_network

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)

def test_pipelines_get():
    from pyxnat.core import pipelines
    p = pipelines.Pipelines('nosetests3', central)
    print(p.get())
