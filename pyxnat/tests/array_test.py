import unittest
import os.path as op
from pyxnat import Interface
from . import PYXNAT_SKIP_NETWORK_TESTS
from nose import SkipTest

import logging as log
log.basicConfig(level=log.INFO)

class ArrayTests(unittest.TestCase):
    ''' Resource-related XNAT connectivity test cases '''

    def setUp(self):
        self._interface = Interface(config=op.join(op.dirname(op.abspath(__file__)), 'central.cfg'))

    def test_array_experiments(self):
        '''
        Get a list of experiments from a given subject which has multiple types
        of experiments (i.e. MRSessions and PETSessions) and assert it gathers
        them all.
        '''
        if PYXNAT_SKIP_NETWORK_TESTS:
            raise SkipTest('No network. Skipping test.')
        e = self._interface.array.experiments(subject_id='CENTRAL_S06242').data
        self.assertGreaterEqual(len(e), 3)

    def test_array_mrsessions(self):
        '''
        From a given subject which has multiple types of experiments, get a list
        of MRI sessions and assert its length matches the list of experiments of
        type 'xnat:mrSessionData'
        '''
        if PYXNAT_SKIP_NETWORK_TESTS:
            raise SkipTest('No network. Skipping test.')
        mris = self._interface.array.mrsessions(subject_id='CENTRAL_S06242').data
        exps = self._interface.array.experiments(subject_id='CENTRAL_S06242',
                                                 experiment_type='xnat:mrSessionData'
                                                 ).data
        self.assertListEqual(mris, exps)

    def test_array_scans(self):
        '''
        Get a list of scans from a given experiment which has multiple types
        of scans (i.e. PETScans and CTScans) and assert it gathers them all.
        '''
        if PYXNAT_SKIP_NETWORK_TESTS:
            raise SkipTest('No network. Skipping test.')
        s = self._interface.array.scans(experiment_id='CENTRAL_E72012').data
        self.assertEqual(len(s),16)

    def test_array_mrscans(self):
        '''
        Get a list of MRI scans from a given experiment which has multiple scans
        mixed (i.e. MRScans and MRSpectroscopies, aka OtherDicomScans) and
        assert its length matches the list of scans filtered by type 'xnat:mrScanData'
        '''
        if PYXNAT_SKIP_NETWORK_TESTS:
            raise SkipTest('No network. Skipping test.')
        mris = self._interface.array.mrscans(experiment_id='CENTRAL_E72012').data
        exps = self._interface.array.scans(experiment_id='CENTRAL_E72012',
                                           scan_type='xnat:mrScanData'
                                           ).data
        self.assertListEqual([i['xnat:mrscandata/id'] for i in mris],
                             [i['xnat:mrscandata/id'] for i in exps])

    def test_search_experiments(self):
        if PYXNAT_SKIP_NETWORK_TESTS:
            raise SkipTest('No network. Skipping test.')
        res = self._interface.array.search_experiments(project_id='nosetests3',
            experiment_type='xnat:subjectData').data
        self.assertGreaterEqual(len(res), 1)
