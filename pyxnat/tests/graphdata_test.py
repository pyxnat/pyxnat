from pyxnat.core.help import GraphData, PaintGraph, SchemasInspector
from .. import Interface
import os.path as op
central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_graphdata():
    g = GraphData(central)
    g.architecture()
    g.datatypes()
    g.rest_resource('projects')

def test_schemasinspector():
    si = SchemasInspector(central)
    si()

def test_paintgraph():
    pg = PaintGraph(central)
    # needs pygraphviz
    #pg.architecture()
