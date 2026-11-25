import os.path as op
from pyxnat import Interface

fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)


def test_ashs_volumes():
    r = central.select.experiment('BBRCDEV_E03094').resource('ASHS')
    hv = r.volumes()
    v = hv.query('region=="CA1" & side=="left"')['volume'].tolist()[0]
    assert (v == 1287.675)
