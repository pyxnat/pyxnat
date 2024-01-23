from pyxnat import Interface

#fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
#central = Interface(config=fp)
central = Interface('https://www.nitrc.org/ir', anonymous=True)


def test_inspector_structure():
    from pyxnat.core import Inspector
    i = Inspector(central)
    i.set_autolearn()
    print(i.datatypes())
    i.structure()
