XNAT_RESOURCE_NAMES = ['FREESURFER6', 'FREESURFER6_HIRES']

def hippoSfVolumes(self, mode='T1'):
    import pandas as pd

    table = []
    files = list(self.files('*h.hippoSfVolumes-%s.v10.txt'%mode))
    for f in files:
        uri = f._uri

        res = self._intf.get(uri).text.split('\n')
        d1 = dict([each.split(' ') for each in res[:-1]])
        d2 = dict([('%s'%k, float(v)) \
                   for k,v in d1.items()])

        side = {'l':'left', 'r':'right'}[uri.split('/')[-1][0]]
        for region, value in d2.items():
            row = [side, region, value]
            table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)



def aparc(self):
    import pandas as pd

    volumes = ['BrainSegVol', 'BrainSegVolNotVent', 'BrainSegVolNotVentSurf',
        'CortexVol', 'SupraTentorialVol', 'SupraTentorialVolNotVent','eTIV']

    unitless = ['NumVert']

    surfaces = ['WhiteSurfArea']

    thickness = ['MeanThickness']

    columns = ['StructName', 'NumVert', 'SurfArea', 'GrayVol', 'ThickAvg',
        'ThickStd', 'MeanCurv', 'GausCurv', 'FoldInd', 'CurvInd']

    table = []
    files = list(self.files('*h.aparc.stats'))
    for f in files:

        uri = f._uri
        side = {'l':'left', 'r':'right'}[uri.split('/')[-1][0]]

        res = self._intf.get(uri).text.split('\n')

        res2 = [e for e in res if e.startswith('# Measure ')]
        for each in volumes:
            m = float([e for e in res2 if each in e.split(', ')[1]][0].split(', ')[-2])
            table.append([None, 'Volume_mm3', each, m])

        for each in thickness:
            m = float([e for e in res2 if each in e.split(', ')[1]][0].split(', ')[-2])
            table.append([None, 'Thickness_mm', each, m])

        for each in surfaces:
            m = float([e for e in res2 if each in e.split(', ')[1]][0].split(', ')[-2])
            table.append([None, 'SurfArea_mm2', each, m])

        for each in unitless:
            m = float([e for e in res2 if each in e.split(', ')[1]][0].split(', ')[-2])
            table.append([None, 'unitless', each, m])

        res2 = [e for e in res if not e.startswith('#')]
        d2 = [[each for each in e.split(' ') if each != ''] for e in res2]
        d3 = pd.DataFrame(d2, columns=columns).dropna().set_index('StructName').to_dict()

        for m, aparc in d3.items():
            for region, value in aparc.items():
                row = [side, m, region, value]
                table.append(row)


    columns = ['side', 'measurement', 'region', 'value']
    return pd.DataFrame(table, columns=columns)

def aseg(self):
    import pandas as pd
    columns = ['Index', 'SegId', 'NVoxels', 'Volume_mm3', 'StructName',
        'normMean', 'normStdDev', 'normMin', 'normMax', 'normRange']

    f = list(self.files('*aseg.stats'))[0]

    uri = f._uri

    res = self._intf.get(uri).text.split('\n')

    volumes = ['BrainSegVol', 'BrainSegVolNotVent', 'BrainSegVolNotVentSurf',
        'VentricleChoroidVol', 'lhCortexVol', 'rhCortexVol', #'Cortex',
        'lhCerebralWhiteMatterVol', 'rhCerebralWhiteMatterVol',
        'CerebralWhiteMatterVol', 'SubCortGrayVol', 'TotalGrayVol', 'SupraTentorialVol',
        'SupraTentorialVolNotVent', 'SupraTentorialVolNotVentVox',
        'MaskVol', 'eTIV']

    unitless = ['BrainSegVol-to-eTIV', 'MaskVol-to-eTIV', 'lhSurfaceHoles',
    'rhSurfaceHoles', 'SurfaceHoles']

    table = []
    res2 = [e for e in res if e.startswith('# Measure ')]
    for each in volumes:
        #[e for e in res2 if each == e.split(', ')[1]]
        m = float([e for e in res2 if each == e.split(', ')[1]][0].split(', ')[-2])
        table.append(['Volume_mm3', each, m])

    for each in unitless:
        m = float([e for e in res2 if each == e.split(', ')[1]][0].split(', ')[-2])
        table.append(['unitless', each, m])

    res2 = [e for e in res if not e.startswith('#')]
    d2 = [[each for each in e.split(' ') if each != ''] for e in res2]
    d3 = pd.DataFrame(d2, columns=columns).dropna().set_index('StructName').to_dict()

    for m, aseg in d3.items():
        for region, value in aseg.items():
            row = [m, region, value]
            table.append(row)

    columns = ['measurement', 'region', 'value']
    return pd.DataFrame(table, columns=columns)


def normMean(self):

    from roistats import collect
    import pandas as pd
    f1 = list(self.files('*mri/aparc.a2009s+aseg.mgz'))[0]
    f2 = list(self.files('*mri/norm.mgz'))[0]
    s_label = f2._uri.split('/')[-3]
    e_id = f2._uri.split('/')[-7]
    f1.get('/tmp/aparc.mgz')
    f2.get('/tmp/T1.mgz')
    import json
    lut = dict([(int(e),v) for e,v in json.load(open('/tmp/d.json')).items()])
    roi_values = collect.roistats_from_maps(['/tmp/norm.mgz'], '/tmp/aparc.mgz',
        subjects=[(e_id, s_label)])
    df = pd.DataFrame(roi_values, columns=lut)
    return df.rename(columns=lut)
