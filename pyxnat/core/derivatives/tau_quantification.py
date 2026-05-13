XNAT_RESOURCE_NAMES = ['TAU_QUANTIFICATION']


def quantification_results(self):
    """Return Tau PET quantification results as a pandas DataFrame"""
    import pandas as pd
    from io import StringIO

    f = self.file('tau_quantification_results.csv')
    content = self._intf.get(f._uri).text
    df = pd.read_csv(StringIO(content))
    return df


def regional_quantification(self, optimization='harmonized', measurement='suvr',
                            atlas='hammers'):
    """Return regional Tau PET quantification for one atlas/measurement/optimization"""
    df = self.quantification_results()

    q = 'atlas.str.contains(@atlas, case=False, regex=False)'
    q += ' and measurement == @measurement'
    q += ' and smoothing_type == @optimization'
    df = df.query(q, engine='python')

    if df.empty:
        raise ValueError(f"Empty quantification results for atlas='{atlas}', "
                         f"measurement='{measurement}', optimization='{optimization}'")

    if df['atlas'].nunique(dropna=False) != 1:
        raise ValueError(f"Filter atlas='{atlas}' matched multiple atlas values")

    if df['smoothing_type'].nunique(dropna=False) != 1:
        raise ValueError(f"Filter optimization='{optimization}' matched multiple "
                         f"smoothing_type values")

    return df
