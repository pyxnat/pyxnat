XNAT_RESOURCE_NAME = 'ALPS'


def alps(self):
    """ Returns the average ALPS (Diffusivity Along the Perivascular Space) index
    for both hemispheres, along with the left and right side values and supporting
    metrics."""

    import pandas as pd
    from io import StringIO

    f = self.file('alps.stat/alps.csv')
    content = self._intf.get(f.attributes()['URI']).content.decode('utf-8')
    df = pd.read_csv(StringIO(content))

    # drop empty columns and sort table
    df.drop(columns=['id', 'scanner'], inplace=True)
    return df


def fa_md_alps(self):
    """Returns FA (Fractional Anisotropy) and MD (Mean Diffusivity) diffusion
    metrics measured in the same ROIs used for the ALPS index, for both hemispheres."""

    import pandas as pd
    from io import StringIO

    f = self.file('alps.stat/fa+md_alps.csv')
    content = self._intf.get(f.attributes()['URI']).content.decode('utf-8')
    df = pd.read_csv(StringIO(content))

    # drop empty columns and sort table
    df.drop(columns=['id', 'scanner'], inplace=True)
    return df
