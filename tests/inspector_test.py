from pyxnat import Interface
import os.path as op
from . import skip_if_no_network

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_inspector_structure():
    from pyxnat.core import Inspector
    i = Inspector(central)
    i.set_autolearn()
    print(i.datatypes())
    s = i.structure()
