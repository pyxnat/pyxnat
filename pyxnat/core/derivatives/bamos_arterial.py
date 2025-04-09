XNAT_RESOURCE_NAME = 'BAMOS_ARTERIAL'

def stats(self):
    import pandas as pd
    import sys
    if sys.version_info[0] < 3:
        from StringIO import StringIO
    else:
        from io import StringIO

    f = self.file('bamos_arterial_stats.csv')
    uri = f._uri
    res = self._intf.get(uri).text
    text = StringIO(res)
    df = pd.read_csv(text)
    return df