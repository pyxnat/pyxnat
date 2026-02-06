from pyxnat.core.help import GraphData, PaintGraph, SchemasInspector
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

central = Interface('https://www.nitrc.org/ir', anonymous=True)

@skip_if_no_network
def test_graphdata():
    g = GraphData(central)
    g.architecture()
    g.datatypes()
    g.rest_resource('projects')


@skip_if_no_network
def test_schemasinspector():
    si = SchemasInspector(central)
    si()


def test_paintgraph():
    PaintGraph(central)
