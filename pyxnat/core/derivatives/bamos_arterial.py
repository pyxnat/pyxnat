XNAT_RESOURCE_NAME = 'BAMOS_ARTERIAL'


def stats(self):
    """ Collects descriptive statistics based on the segmented lesions of the
        white matter, including volumes and number of lesions per arterial
        territory. A voxel is considered as a part of a lesion if it has a
        value higher than 0.5."""
    import pandas as pd
    from io import StringIO

    f = self.file('bamos_arterial_stats.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df
