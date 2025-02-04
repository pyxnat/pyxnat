import unittest
from pyxnat import Interface
from pyxnat.tests import skip_if_no_network
import logging as log
log.basicConfig(level=log.INFO)


class ArrayTests(unittest.TestCase):
    ''' Resource-related XNAT connectivity test cases '''

    def setUp(self):
        self._intf = Interface('https://www.nitrc.org/ir', anonymous=True)

    @skip_if_no_network
    def test_array_experiments(self):
        '''
        Get a list of experiments from a given subject which has multiple types
        of experiments (i.e. MRSessions and PETSessions) and assert it gathers
        them all.
        '''
        e = self._intf.array.experiments(subject_id='xnat_S02636').data
        self.assertEqual(len(e), 1)

    @skip_if_no_network
    def test_array_mrsessions(self):
        '''
        From a given subject which has multiple types of experiments, get a
        list of MRI sessions and assert its length matches the list of
        experiments of type 'xnat:mrSessionData'
        '''
        mris = self._intf.array.mrsessions(subject_id='xnat_S02636').data
        e = self._intf.array.experiments(subject_id='xnat_S02636',
                                         experiment_type='xnat:mrSessionData')
        exps = e.data
        self.assertListEqual(mris, exps)

    @skip_if_no_network
    def test_array_scans(self):
        '''
        Get a list of scans from a given experiment which has multiple types
        of scans (i.e. PETScans and CTScans) and assert it gathers them all.
        '''
        s = self._intf.array.scans(experiment_id='xnat_E02685').data
        self.assertEqual(len(s), 1)

    @skip_if_no_network
    def test_array_mrscans(self):
        '''
        Get a list of MRI scans from a given experiment which has multiple
        scans mixed (i.e. MRScans and MRSpectroscopies, aka OtherDicomScans)
        and assert its length matches the list of scans filtered by type
        'xnat:mrScanData'
        '''
        mris = self._intf.array.mrscans(experiment_id='NITRC_IR_E10539').data
        exps = self._intf.array.scans(experiment_id='NITRC_IR_E10539',
                                      scan_type='xnat:mrScanData').data
        self.assertListEqual([i['xnat:mrscandata/id'] for i in mris],
                             [i['xnat:mrscandata/id'] for i in exps])

    @skip_if_no_network
    def test_search_experiments(self):
        et = 'xnat:subjectData'
        e = self._intf.array.search_experiments(project_id='ixi',
                                                experiment_type=et)
        res = e.data
        self.assertEqual(len(res), 584)
