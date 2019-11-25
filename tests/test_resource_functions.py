import os.path as op
from pyxnat import Interface

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')

central = Interface(config=fp)

def test_ashs_volumes():
    r = central.select.experiment('CENTRAL04_E00637').resource('ASHS')
    hv = r.volumes()
    v = hv.query('region=="CA1" & side=="left"')['volume'].tolist()[0]
    assert(v == 1585.838)
