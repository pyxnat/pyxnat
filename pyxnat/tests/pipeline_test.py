import unittest
import os.path as op
import json
import os
from pyxnat import Interface

import logging as log
log.basicConfig(level=log.INFO)


class XNATConnectionResources(unittest.TestCase):
    ''' Resource-related XNAT connectivity test cases '''

    def setUp(self):
        self._intf = Interface(config='.xnat.cfg')

    def test_run_pipeline(self):
        '''
        Run a pipeline, collect execution info and check that
        current datetime and launch datetime are close.
        '''
        import datetime
        import dateparser

        now = datetime.datetime.utcnow()
        p = self._intf.select.experiment('BBRCDEV_E00014').run('archiving_validation',
                                            params={'notify':'N'})
        exec_details = p.info('BBRCDEV_E00014')
        settings = {'TIMEZONE': 'CET', 'TO_TIMEZONE': 'UTC'}
        launch_time = dateparser.parse(exec_details['launch_time'],settings=settings)
        self.assertAlmostEqual(now,launch_time,delta=datetime.timedelta(seconds=2))

def test_pipeline_aliases():
    central = Interface(config=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'central.cfg'))
    stepId = central.select.project('nosetests').pipelines.aliases()
    assert stepId == {'DicomToNifti': 'DicomToNifti'}
