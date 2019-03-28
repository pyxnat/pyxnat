import unittest
from pyxnat import Interface

import logging as log
log.basicConfig(level=log.INFO)

class ArrayTests(unittest.TestCase):
    ''' Resource-related XNAT connectivity test cases '''

    def setUp(self):
        self._interface = Interface(config='.xnat.cfg')

    def test_array_experiments(self):
        '''
        Get a list of experiments from a given subject which has multiple types
        of experiments (i.e. MRSessions and PETSessions) and assert it gathers
        them all.
        '''

        e = self._interface.array.experiments(subject_id='BBRCDEV_S00245').data
        self.assertGreaterEqual(len(e),3)

    def test_array_mrsessions(self):
        '''
        From a given subject which has multiple types of experiments, get a list
        of MRI sessions and assert its length matches the list of experiments of
        type 'xnat:mrSessionData'
        '''

        mris = self._interface.array.mrsessions(subject_id='BBRCDEV_S00245').data
        exps = self._interface.array.experiments(subject_id='BBRCDEV_S00245',
                                                 experiment_type='xnat:mrSessionData'
                                                 ).data
        self.assertListEqual(mris,exps)

    def test_array_scans(self):
        '''
        Get a list of scans from a given experiment which has multiple types
        of scans (i.e. PETScans and CTScans) and assert it gathers them all.
        '''

        s = self._interface.array.scans(experiment_id='BBRCDEV_E00745').data
        self.assertEqual(len(s),3)

    def test_array_mrscans(self):
        '''
        Get a list of MRI scans from a given experiment which has multiple scans
        mixed (i.e. MRScans and MRSpectroscopies, aka OtherDicomScans) and
        assert its length matches the list of scans filtered by type 'xnat:mrScanData'
        '''

        mris = self._interface.array.mrscans(experiment_id='BBRCDEV_E00398').data
        exps = self._interface.array.scans(experiment_id='BBRCDEV_E00398',
                                           scan_type='xnat:mrScanData'
                                           ).data
        self.assertListEqual([i['xnat:mrscandata/id'] for i in mris],
                             [i['xnat:mrscandata/id'] for i in exps])
