XNAT_RESOURCE_NAMES = ['FDG_QUANTIFICATION', 'FDG_QUANTIFICATION2']


def quantification_results(self):
    import pandas as pd
    import sys
    if sys.version_info[0] < 3:
        from StringIO import StringIO
    else:
        from io import StringIO

    f = self.file('quantification_results.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df


def landau_signature(self, optimized=False, reference_region='vermis'):
    """Returns the AD signature obtained from FDG as described in
    Landau et al., Ann Neurol., 2012."""

    df = self.quantification_results()
    q = 'region == "landau_Composite" &'\
        ' reference_region == "{reference_region}" &'\
        ' measurement == "suvr"'.format(reference_region=reference_region)

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    return float(df.query(q)['value'].iloc[0])


def regional_quantification(self, optimized=True, reference_region='vermis', 
                            atlas='hammers'):
    df = self.quantification_results()

    q = 'reference_region == "{reference_region}" &'\
        ' atlas.str.lower().str.contains("{atlas}", regex=False) &'\
        ' measurement == "suvr"'.format(reference_region=reference_region,
                                        atlas=atlas)

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    df = df.query(q, engine='python')

    assert len(set(df['atlas'])) == 1
    assert len(set(df['optimized_pet'])) == 1

    return df
