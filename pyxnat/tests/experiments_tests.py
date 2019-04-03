import os
import os.path as op

from .. import Interface

_modulepath = os.path.dirname(os.path.abspath(__file__))

central = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

def test_global_experiment_listing():
    assert central.array.experiments(project_id='CENTRAL_OASIS_CS',
                                     experiment_type='xnat:mrSessionData',
                                     )
