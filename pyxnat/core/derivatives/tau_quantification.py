XNAT_RESOURCE_NAMES = ['TAU_QUANTIFICATION']

def quantification_results(self):
    import pandas as pd
    from io import StringIO

    f = self.file('tau_quantification_results.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df


def regional_quantification(self, optimization='harmonized', measurement='suvr',
                            atlas='aparc+aseg'):
    df = self.quantification_results()

    q = f'atlas.str.lower().str.contains("{atlas}", regex=False)'
    q += f' and measurement == "{measurement}"'
    q += f' and smoothing_type == "{optimization}"'
    df = df.query(q, engine='python')

    assert len(set(df['atlas'])) == 1
    assert len(set(df['smoothing_type'])) == 1

    return df