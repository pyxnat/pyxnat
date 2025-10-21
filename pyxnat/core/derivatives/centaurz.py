XNAT_RESOURCE_NAMES = ['CENTAURZ']

def quantification_results(self):
    import pandas as pd
    import sys
    if sys.version_info[0] < 3:
        from StringIO import StringIO
    else:
        from io import StringIO

    f = self.file('centaurz_quantification_results.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df


def centaurz(self):
    df = self.quantification_results()
    q = ' measurement == "centaurz"'

    return float(df.query(q)['value'].iloc[0])