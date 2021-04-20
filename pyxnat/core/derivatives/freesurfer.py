XNAT_RESOURCE_NAMES = ['FREESURFER6', 'FREESURFER6_HIRES', 'FREESURFER7']


def amygNucVolumes(self, mode='T1'):
    """Returns amygdala nuclei volumetry as estimated by FreeSurfer
    `recon-all`."""
    import pandas as pd

    if self.label().startswith('FREESURFER6'):
        raise NotImplementedError('Not available in FreeSurfer 6')

    table = []
    files = list(self.files('*h.amygNucVolumes-%s.v*.txt' % mode))
    for f in files:
        uri = f._uri

        res = self._intf.get(uri).text.split('\n')
        d1 = dict([each.split(' ') for each in res[:-1]])
        d2 = dict([('%s' % k, float(v))
                  for k, v in d1.items()])

        side = {'l': 'left', 'r': 'right'}[uri.split('/')[-1][0]]
        for region, value in d2.items():
            row = [side, region, value]
            table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)


def hippoSfVolumes(self, mode='T1'):
    """Returns hippocampal subfield volumetry as estimated by FreeSurfer
    `recon-all`."""
    import pandas as pd

    table = []
    files = list(self.files('*h.hippoSfVolumes-%s.v*.txt' % mode))
    for f in files:
        uri = f._uri

        res = self._intf.get(uri).text.split('\n')
        d1 = dict([each.split(' ') for each in res[:-1]])
        d2 = dict([('%s' % k, float(v))
                  for k, v in d1.items()])

        side = {'l': 'left', 'r': 'right'}[uri.split('/')[-1][0]]
        for region, value in d2.items():
            row = [side, region, value]
            table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)


def aparc(self, atlas='desikan-killiany'):
    """Returns cortical features as estimated by FreeSurfer `recon-all`."""

    import pandas as pd

    volumes = ['BrainSegVol', 'BrainSegVolNotVent', 'BrainSegVolNotVentSurf',
               'CortexVol', 'SupraTentorialVol', 'SupraTentorialVolNotVent',
               'eTIV']

    unitless = ['NumVert']

    surfaces = ['WhiteSurfArea']

    thickness = ['MeanThickness']

    columns = ['StructName', 'NumVert', 'SurfArea', 'GrayVol', 'ThickAvg',
               'ThickStd', 'MeanCurv', 'GausCurv', 'FoldInd', 'CurvInd']

    table = []
    if atlas == 'desikan-killiany':
        ft = 'aparc'
    elif atlas == 'destrieux':
        ft = 'aparc.a2009s'
    else:
        raise Exception('Invalid atlas "%s". Should be either '
                        'desikan-killiany or destrieux.' % atlas)

    files = list(self.files('*h.%s.stats' % ft))
    for f in files:

        uri = f._uri
        side = {'l': 'left', 'r': 'right'}[uri.split('/')[-1][0]]

        res = self._intf.get(uri).text.split('\n')

        res2 = [e for e in res if e.startswith('# Measure ')]

        measurements = {'Volume_mm3': volumes,
                        'Thickness_mm': thickness,
                        'SurfArea_mm2': surfaces,
                        'unitless': unitless}

        for unit, data in measurements.items():
            for each in data:
                m = [e for e in res2 if each == e.split(', ')[1]]
                if len(m) == 1:
                    m = float(m[0].split(', ')[-2])
                    table.append([None, unit, each, m])        

        res2 = [e for e in res if not e.startswith('#')]
        d2 = [[each for each in e.split(' ') if each != ''] for e in res2]
        d2 = pd.DataFrame(d2, columns=columns).dropna()
        d3 = d2.set_index('StructName').to_dict()

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
               'VentricleChoroidVol', 'lhCortexVol', 'rhCortexVol',  # 'Cortex'
               'lhCerebralWhiteMatterVol', 'rhCerebralWhiteMatterVol',
               'CerebralWhiteMatterVol', 'SubCortGrayVol', 'TotalGrayVol',
               'SupraTentorialVol', 'SupraTentorialVolNotVent',
               'SupraTentorialVolNotVentVox', 'MaskVol', 'eTIV']
    if self.label() == 'FREESURFER7':
        deprecated = ['BrainSegVolNotVentSurf', 'SupraTentorialVolNotVentVox']
        volumes = [v for v in volumes if v not in deprecated]

    unitless = ['BrainSegVol-to-eTIV', 'MaskVol-to-eTIV', 'lhSurfaceHoles',
                'rhSurfaceHoles', 'SurfaceHoles']

    table = []
    res2 = [e for e in res if e.startswith('# Measure ')]
    for each in volumes:
        # [e for e in res2 if each == e.split(', ')[1]]
        m = float([e for e in res2
                   if each == e.split(', ')[1]][0].split(', ')[-2])
        table.append(['Volume_mm3', each, m])

    for each in unitless:
        m = float([e for e in res2
                   if each == e.split(', ')[1]][0].split(', ')[-2])
        table.append(['unitless', each, m])

    res2 = [e for e in res if not e.startswith('#')]
    d2 = [[each for each in e.split(' ') if each != ''] for e in res2]
    d2 = pd.DataFrame(d2, columns=columns).dropna()
    d3 = d2.set_index('StructName').to_dict()

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
    lut = dict([(int(e), v)
               for e, v in json.load(open('/tmp/d.json')).items()])
    roi_values = collect.roistats_from_maps(['/tmp/norm.mgz'],
                                            '/tmp/aparc.mgz',
                                            subjects=[(e_id, s_label)])
    df = pd.DataFrame(roi_values, columns=lut)
    return df.rename(columns=lut)
