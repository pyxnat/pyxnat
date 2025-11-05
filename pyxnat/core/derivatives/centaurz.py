XNAT_RESOURCE_NAMES = ['CENTAURZ']


def quantification_results(self):
    import pandas as pd
    from io import StringIO

    f = self.file('centaurz_quantification_results.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df


def centaurz(self, optimization='harmonized'):
    """Return the CenTauRz metric for the "Universal" region and given
    optimization type. The default optimization ("harmonized") ensures
    generalizability and robustness across tracers, scanners and projects."""
    df = self.quantification_results()
    q = 'region == "Universal" and measurement == "centaurz"'
    q += f' and smoothing_type == "{optimization}"'
    return float(df.query(q)['value'].iloc[0])
