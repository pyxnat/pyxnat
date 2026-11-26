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


def coverage(self, atlas='DK'):
    """Return parcel coverage fractions for the atlas, indexed by parcel name."""

    import pandas as pd
    from io import StringIO

    files = list(self.files(f'*_atlas-{atlas}_coverage.tsv'))
    if not files:
        raise FileNotFoundError(f"No XCP-D coverage TSV file found for atlas '{atlas}'.")
    if len(files) > 1:
        raise ValueError(f"Multiple XCP-D coverage TSV files found for atlas '{atlas}'.")

    content = self._intf.get(files[0]._uri).content.decode('utf-8')
    return pd.read_table(StringIO(content), index_col='Node')


def qc(self):
    """Return the XCP-D run-level QC summary."""

    import pandas as pd
    from io import StringIO

    files = list(self.files('*_desc-linc_qc.csv'))
    if not files:
        raise FileNotFoundError('No XCP-D LINC QC CSV file found.')
    if len(files) > 1:
        raise ValueError('Multiple XCP-D LINC QC CSV files found.')

    content = self._intf.get(files[0]._uri).content.decode('utf-8')
    return pd.read_csv(StringIO(content))


def motion(self):
    """Return per-volume motion parameters and framewise displacement."""

    import pandas as pd
    from io import StringIO

    files = list(self.files('*_motion.tsv'))
    if not files:
        raise FileNotFoundError('No XCP-D motion TSV file found.')
    if len(files) > 1:
        raise ValueError('Multiple XCP-D motion TSV files found.')

    content = self._intf.get(files[0]._uri).content.decode('utf-8')
    return pd.read_table(StringIO(content))

