from pyxnat.core.help import GraphData, PaintGraph, SchemasInspector
from .. import Interface
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest
import os.path as op
central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_graphdata():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    g = GraphData(central)
    g.architecture()
    g.datatypes()
    g.rest_resource('projects')

def test_schemasinspector():
    if PYXNAT_SKIP_NETWORK_TESTS:
        raise SkipTest('No network. Skipping test.')
    si = SchemasInspector(central)
    si()

def test_paintgraph():
    pg = PaintGraph(central)
    # needs pygraphviz
    #pg.architecture()
