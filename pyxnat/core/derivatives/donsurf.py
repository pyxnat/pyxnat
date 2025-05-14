XNAT_RESOURCE_NAME = 'DONSURF'


def aparc(self, metric='GM-MD'):
    """
    Retrieves cortical features as estimated by `DONSURF`.

    Parameters
    ----------
    metric : str, optional
        DONSURF metric to retrieve aparc statistics for. Available metrics
        are 'GM-MD', 'GM-MD-koo', and 'SWM-MD'. Defaults to 'GM-MD'.

    Returns
    -------
    pandas.DataFrame
        Cortical DONSURF features for the selected `metric`.
    """

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
    if metric not in ['GM-MD', 'SWM-MD', 'GM-MD-koo']:
        raise Exception(f'Invalid DONSURF metric "{metric}".')

    files = list(self.files(f'{metric}/stats/*h.aparc.stats'))
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
