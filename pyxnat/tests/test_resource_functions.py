import os.path as op
from pyxnat import Interface

fp = op.abspath('.devxnat.cfg')
central = Interface(config=fp)
p = central.select.project('pyxnat_tests')
s = p.subject('rs')
e1 = s.experiment('BBRCDEV_E03094')

p = central.select.project('pyxnat_tests')
s = p.subject('BBRCDEV_S02627')
e2 = s.experiment('BBRCDEV_E03106')


def test_ashs_volumes():
    r = e1.resource('ASHS')
    hv = r.volumes()
    v = hv.query('region=="CA1" & side=="left"')['volume'].tolist()[0]
    assert (v == 1287.675)


def test_freesurfer6_aparc():
    r = e1.resource('FREESURFER6')
    hv = r.aparc()
    q = 'region=="supramarginal" & side=="left" & measurement=="CurvInd"'
    v = hv.query(q)['value'].tolist()[0]
    assert(v == '10.8')


def test_freesurfer6_aseg():
    r = e1.resource('FREESURFER6')
    hv = r.aseg()
    v = hv.query('region=="BrainSegVol"')['value'].tolist()[0]
    assert(v == 2463095.0)


def test_scandate():
    s = e2.scans().first()
    r = s.resource('DICOM')
    assert(r.scandate() == '2008-05-06')


def test_ftm_quantification():
    r = e1.resource('FTM_QUANTIFICATION')
    c1 = r.centiloids(optimized=True)
    c2 = r.centiloids()
    assert c1 == -6.731959667125082
    assert c2 == -7.958670071142706


def test_ftm_regional_quantification():
    r = e1.resource('FTM_QUANTIFICATION2')
    rq1 = r.regional_quantification().\
        query('region == "Hippocampus_l"')
    rq2 = r.regional_quantification(atlas='aal', reference_region='pons').\
        query('region == "Hippocampus_L"')
    assert rq1.shape == rq2.shape == (1, 8)
    assert rq1.optimized_pet.iloc[0]
    assert rq1.atlas.iloc[0] == "hammers"
    assert rq1.reference_region.iloc[0] == "whole_cerebellum"
    assert rq1.value.iloc[0] == 1.0497374534606934
    assert rq2.atlas.iloc[0] == "aal"
    assert rq2.reference_region.iloc[0] == "pons"
    assert rq2.value.iloc[0] == 0.6280973553657532


def test_fdg_quantification():
    r = e1.resource('FDG_QUANTIFICATION')
    c1 = r.landau_signature(optimized=True)
    c2 = r.landau_signature()
    assert c1 == 1.2596989870071411
    assert c2 == 1.2491936683654783


def test_fdg_regional_quantification():
    r = e1.resource('FDG_QUANTIFICATION2')
    rq1 = r.regional_quantification(). \
        query('region == "Hippocampus_l"')
    rq2 = r.regional_quantification(atlas='aal', reference_region='pons'). \
        query('region == "Hippocampus_L"')
    assert rq1.shape == rq2.shape == (1, 8)
    assert rq1.optimized_pet.iloc[0]
    assert rq1.atlas.iloc[0] == "hammers"
    assert rq1.reference_region.iloc[0] == "vermis"
    assert rq1.value.iloc[0] == 1.058446764945984
    assert rq2.atlas.iloc[0] == "aal"
    assert rq2.reference_region.iloc[0] == "pons"
    assert rq2.value.iloc[0] == 1.093239426612854


def test_bamos_volume():
    r = e1.resource('BAMOS')
    v = r.volume()
    assert(v == 33620.32498628937)


def test_bamos_stats():
    r = e1.resource('BAMOS')
    v = r.stats()
    assert(sum(v['volume']) == 33620.32429030311)
    fig, ax = r.bullseye_plot(stats=v)
    
    import matplotlib
    assert(isinstance(fig, matplotlib.figure.Figure))


def test_bamos_n_lesion():
    r = e1.resource('BAMOS')
    v = r.n_lesions()
    assert(v == 296)


def test_freesurfer7_amygNucVolumes():
    r = e1.resource('FREESURFER7')
    hv = r.amygNucVolumes()
    assert (hv.shape == (20, 3))
    q = 'region=="Whole_amygdala" & side=="left"'
    v = hv.query(q)['value'].tolist()[0]
    assert(v == 1426.132879)


def test_freesurfer7_hippoSfVolumes():
    r = e1.resource('FREESURFER7')
    hv = r.hippoSfVolumes()
    assert (hv.shape == (44, 3))
    q = 'region=="Whole_hippocampus" & side=="left"'
    v = hv.query(q)['value'].tolist()[0]
    assert(v == 2853.846782)


def test_freesurfer7_aparc():
    r = e1.resource('FREESURFER7')
    hv = r.aparc()
    assert (hv.shape == (632, 4))
    q = 'region=="supramarginal" & side=="left" & measurement=="CurvInd"'
    v = hv.query(q)['value'].tolist()[0]
    assert(v == '5.0')


def test_freesurfer7_aseg():
    r = e1.resource('FREESURFER7')
    hv = r.aseg()
    assert (hv.shape == (424, 3))
    v = hv.query('region=="BrainSegVol"')['value'].tolist()[0]
    assert(v == 906719.90625)


def test_spm12_volumes():
    r = e1.resource('SPM12_SEGMENT')
    v = r.volumes()
    assert(v['c1'] > v['c2'] > v['c3'])


def test_cat12_volumes():
    r = e1.resource('CAT12_SEGMENT')
    v = r.volumes()
    assert(v['mri/p1'] > v['mri/p2'] > v['mri/p3'])


def test_donsurf():
    r = e1.resource('DONSURF')
    st = r.aparc()
    left = float(st.query('measurement == "CurvInd" &'\
                          'region == "insula" & side == "left"')['value'])
    right = float(st.query('measurement == "CurvInd" &'\
                           'region == "insula" & side == "right"')['value'])
    assert(left == 15.7 and right == 15.8)


def test_freesurfer7_extras_brainstem_volumes():
    r = e1.resource('FREESURFER7_EXTRAS')
    bs = r.brainstem_substructures_volumes()
    assert(bs.shape == (5, 2))
    q = 'region=="Medulla"'
    v = bs.query(q)['value'].tolist()[0]
    assert(v == 4427.713893)


def test_freesurfer7_extras_thalamic_volumes():
    r = e1.resource('FREESURFER7_EXTRAS')
    tn = r.thalamic_nuclei_volumes()
    assert(tn.shape == (52, 3))
    q = 'region=="Whole_thalamus" & side=="left"'
    v = tn.query(q)['value'].tolist()[0]
    assert(v == 5248.549485)


def test_freesurfer7_extras_hypothalamic_volumes():
    r = e1.resource('FREESURFER7_EXTRAS')
    hs = r.hypothalamic_subunits_volumes()
    assert(hs.shape == (12, 3))
    q = 'region=="posterior" & side=="right"'
    v = hs.query(q)['value'].tolist()[0]
    assert(v == 64.84)


def test_basil_volumes():
    r = e1.resource('BASIL')
    v = r.volumes()
    # assert GM > WM > CSF
    assert(v['T1_fast_pve_1'] > v['T1_fast_pve_2'] > v['T1_fast_pve_0'])


def test_basil_perfusion():
    r = e1.resource('BASIL')
    perf = r.perfusion()
    assert(perf.shape == (12, 4))
    q = 'pvcorr==True & measurement=="perfusion_calib_gm_mean"'
    gm_perf = perf.query(q)['value'].item()
    q = 'pvcorr==True & measurement=="perfusion_calib_wm_mean"'
    wm_perf = perf.query(q)['value'].item()
    assert(gm_perf > wm_perf)


def test_basil_stats():
    r = e1.resource('BASIL')
    stats = r.stats()
    assert(stats.shape == (219, 9))
    q = 'region_analysis=="GM" & name=="Left Hippocampus"'
    nvoxels_gm = stats.query(q)['Nvoxels'].item()
    q = 'region_analysis=="WM" & name=="Left Hippocampus"'
    nvoxels_wm = stats.query(q)['Nvoxels'].item()
    assert(nvoxels_gm > nvoxels_wm)


def test_qsmxt_stats():
    r = e1.resource('QSMXT')
    stats = r.stats()

    q = 'roi == "Left-Pallidum"'
    lh_pallidum = stats.query(q)['mean'].item()
    assert (lh_pallidum > 0)
    q = 'roi == "Right-Pallidum"'
    rh_pallidum = stats.query(q)['mean'].item()
    assert (rh_pallidum > 0)


def test_mrtrix3_conmat():
    r = e1.resource('MRTRIX3')
    df = r.conmat()
    assert df['Left-Hippocampus']['ctx-lh-parahippocampal'] > 2.0
    assert df['Right-Hippocampus']['ctx-rh-parahippocampal'] > 2.0


def test_xcp_d_conmat():
    r = e1.resource('XCP_D')
    df = r.conmat(atlas='DK')
    assert df['Left-Hippocampus']['Right-Hippocampus'] > 0.7
    assert df.shape == (109, 109)

    df2 = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
    assert df2.shape == (99, 99)
    assert set(df.columns).difference(df2.columns) == {'Optic-Chiasm',
                                                       'ctx-lh-frontalpole',
                                                       'ctx-lh-lateralorbitofrontal',
                                                       'ctx-lh-medialorbitofrontal',
                                                       'ctx-lh-temporalpole',
                                                       'ctx-rh-entorhinal',
                                                       'ctx-rh-frontalpole',
                                                       'ctx-rh-lateralorbitofrontal',
                                                       'ctx-rh-medialorbitofrontal',
                                                       'ctx-rh-temporalpole'}


def test_xcp_d_timeseries():
    r = e1.resource('XCP_D')
    df = r.conmat(atlas='DK')
    ts = r.timeseries(atlas='DK')
    assert ts.shape == (287, 109)
    assert df.shape[0] == ts.shape[1]

    df2 = df.dropna(axis=0, how='all').dropna(axis=1, how='all')
    ts2 = ts.dropna(axis=0, how='all').dropna(axis=1, how='all')
    assert ts2.shape == (287, 99)
    assert df2.shape[0] == ts2.shape[1]


def test_3dasl_volumes():
    r = e1.resource('3DASL_QUANTIFICATION')
    v = r.volumes()
    # assert GM > WM > CSF
    assert(v['T1_fast_pve_1'] > v['T1_fast_pve_2'] > v['T1_fast_pve_0'])


def test_3dasl_perfusion():
    r = e1.resource('3DASL_QUANTIFICATION')
    perf = r.perfusion()
    assert(perf.shape == (124, 6))
    q = 'atlas=="global" & region=="GM"'
    gm_perf = perf.query(q)['mean'].item()
    q = 'atlas=="global" & region=="WM"'
    wm_perf = perf.query(q)['mean'].item()
    assert(gm_perf > wm_perf)


def test_alps_alps():
    r = e1.resource('ALPS')
    alps = r.alps()
    assert alps.shape == (1, 11)

    from math import isclose
    assert isclose(alps.alps.iloc[0],
                   (alps.alps_L.iloc[0] + alps.alps_R.iloc[0]) / 2)


def test_alps_fa_md_alps():
    r = e1.resource('ALPS')
    fa_md = r.fa_md_alps()
    fa_md.sort_values(by='diffusion_metric', ascending=True, inplace=True)
    assert fa_md.shape == (2, 7)

    fa_proj, md_proj = fa_md.mean_proj
    fa_assoc, md_assoc = fa_md.mean_assoc
    assert fa_proj > md_proj
    assert fa_assoc > md_assoc
