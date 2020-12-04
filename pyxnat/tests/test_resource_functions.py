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
    r = central.select.experiment('BBRCDEV_E03094').resource('ASHS')
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
    c1 = r.centiloids()
    c2 = r.centiloids(False)
    assert(c1 == -6.731959667125082)
    assert(c2 == -7.958670071142706)


def test_fdg_quantification():
    r = e1.resource('FDG_QUANTIFICATION')
    c1 = r.landau_signature()
    c2 = r.landau_signature(optimized=False)
    assert(c1 == 1.2596989870071411)
    assert(c2 == 1.2491936683654783)


def test_bamos_volume():
    r = e1.resource('BAMOS')
    v = r.volume()
    assert(v == 4874.005882622703)
