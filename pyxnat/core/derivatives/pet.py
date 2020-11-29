XNAT_RESOURCE_NAME = 'PET_QUANTIFICATION'


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


def centiloids(self, optimized=True):
    df = self.quantification_results()
    q = 'region == "cortex" &'\
        'atlas.isna() & reference_region == "whole_cerebellum" &'\
        ' measurement == "centiloid"'

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    return float(df.query(q)['value'])
