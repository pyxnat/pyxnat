XNAT_RESOURCE_NAMES = ['QSMXT']


def stats(self):
    """Summary statistics for the regional QSM values within each structure
    in the FreeSurfer aseg atlas"""
    import csv
    import pandas as pd

    region_stats = []
    cols = []

    f = self.files('region_analysis/*.csv')[0]
    content = self._intf.get(f.attributes()['URI']).text.splitlines()
    for idx, ln in enumerate(csv.reader(content)):
        if idx == 0:
            cols = ln
        else:
            region_stats.append(ln)

    df = pd.DataFrame(region_stats, columns=cols).dropna()
    df['subject_id'] = df['subject'].str.split('_', expand=True)[0].str[4:]
    df['session_id'] = df['subject'].str.split('_', expand=True)[1].str[4:]
    df = df.reindex(['subject_id', 'session_id'] + cols, axis=1)
    for col in ['num_voxels', 'min', 'max', 'median', 'mean', 'std']:
        df[col] = pd.to_numeric(df[col])
    return df
