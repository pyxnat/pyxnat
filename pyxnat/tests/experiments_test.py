from pyxnat import Interface
from pyxnat.tests import skip_if_no_network

#fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
#central = Interface(config=fp)
central = Interface('https://www.nitrc.org/ir', anonymous=True)


@skip_if_no_network
def test_global_experiment_listing():
    assert central.array.experiments(project_id='ixi',
                                     experiment_type='xnat:mrSessionData',
                                     )
