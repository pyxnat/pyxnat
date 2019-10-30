from pyxnat.core.help import GraphData, PaintGraph, SchemasInspector
from pyxnat import Interface
from . import skip_if_no_network
import os.path as op

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

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
    pg = PaintGraph(central)
