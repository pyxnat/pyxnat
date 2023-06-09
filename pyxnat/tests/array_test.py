import unittest
import os.path as op
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network
import logging as log
log.basicConfig(level=log.INFO)


class ArrayTests(unittest.TestCase):
    ''' Resource-related XNAT connectivity test cases '''

    def setUp(self):
        fp = op.join(op.dirname(op.abspath(__file__)), 'central.cfg')
        self._intf = Interface(config=fp)

    @skip_if_no_network
    def test_array_experiments(self):
        '''
        Get a list of experiments from a given subject which has multiple types
        of experiments (i.e. MRSessions and PETSessions) and assert it gathers
        them all.
        '''
        e = self._intf.array.experiments(subject_id='CENTRAL02_S01346').data
        self.assertGreaterEqual(len(e), 3)

    @skip_if_no_network
    def test_array_mrsessions(self):
        '''
        From a given subject which has multiple types of experiments, get a
        list of MRI sessions and assert its length matches the list of
        experiments of type 'xnat:mrSessionData'
        '''
        mris = self._intf.array.mrsessions(subject_id='CENTRAL02_S01346').data
        e = self._intf.array.experiments(subject_id='CENTRAL02_S01346',
                                         experiment_type='xnat:mrSessionData')
        exps = e.data
        self.assertListEqual(mris, exps)

    @skip_if_no_network
    def test_array_scans(self):
        '''
        Get a list of scans from a given experiment which has multiple types
        of scans (i.e. PETScans and CTScans) and assert it gathers them all.
        '''
        s = self._intf.array.scans(experiment_id='CENTRAL03_E05157').data
        self.assertEqual(len(s), 4)

    @skip_if_no_network
    def test_array_mrscans(self):
        '''
        Get a list of MRI scans from a given experiment which has multiple
        scans mixed (i.e. MRScans and MRSpectroscopies, aka OtherDicomScans)
        and assert its length matches the list of scans filtered by type
        'xnat:mrScanData'
        '''
        mris = self._intf.array.mrscans(experiment_id='CENTRAL02_E01892').data
        exps = self._intf.array.scans(experiment_id='CENTRAL02_E01892',
                                      scan_type='xnat:mrScanData').data
        self.assertListEqual([i['xnat:mrscandata/id'] for i in mris],
                             [i['xnat:mrscandata/id'] for i in exps])

    @skip_if_no_network
    def test_search_experiments(self):
        et = 'xnat:subjectData'
        e = self._intf.array.search_experiments(project_id='nosetests5',
                                                experiment_type=et)
        res = e.data
        self.assertGreaterEqual(len(res), 1)
