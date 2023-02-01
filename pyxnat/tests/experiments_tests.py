import os.path as op
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

_modulepath = op.dirname(op.abspath(__file__))

fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
central = Interface(config=fp)


@skip_if_no_network
def test_global_experiment_listing():
    assert central.array.experiments(project_id='CENTRAL_OASIS_CS',
                                     experiment_type='xnat:mrSessionData',
                                     )
