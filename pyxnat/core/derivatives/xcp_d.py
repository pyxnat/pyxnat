XNAT_RESOURCE_NAMES = ['XCP_D']


def conmat(self, atlas='DK'):
    """Returns the functional connectivity matrix from the specified atlas."""
    import pandas as pd
    from io import StringIO

    f = self.files(f'*_atlas-{atlas}_measure-pearsoncorrelation_conmat.tsv')[0]
    content = self._intf.get(f._uri).content.decode('utf-8')
    df = pd.read_table(StringIO(content), sep='\t').drop(columns=['Node'])
    df.index = df.columns
    return df


def timeseries(self, atlas='DK'):
    """Returns the parcellated BOLD time-series from the specified atlas."""
    import pandas as pd
    from io import StringIO

    f = self.files(f'*_atlas-{atlas}_timeseries.tsv')[0]
    content = self._intf.get(f._uri).content.decode('utf-8')
    df = pd.read_table(StringIO(content), sep='\t')

    return df
