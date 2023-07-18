XNAT_RESOURCE_NAMES = ['MRTRIX3']


def conmat(self):
    """Returns the structural connectivity matrix (Desikan-Killiany atlas)."""
    import pandas as pd
    from io import StringIO

    def _get_dk_lut():
        """Retrieves from MRtrix3 sources the lookup table with the relevant
        regions from the default FreeSurfer segmentation (Desikan-Killiany)."""

        url = 'https://raw.githubusercontent.com/MRtrix3/mrtrix3/3.0.4/share/mrtrix3/labelconvert/fs_default.txt'
        cols = ['label_index', 'label_code', 'label', 'R', 'G', 'B', 'n_colors']

        raw_data = self._intf._http.get(url).content.decode('utf-8')
        data = [ln.split() for ln in raw_data.splitlines()
                if ln and ln[0] not in ['#', '0'] and '-Proper ' not in ln]
        return pd.DataFrame(data, columns=cols)

    dk_lut = _get_dk_lut()

    f = self.file('connectome.csv')
    content = self._intf.get(f._uri).content.decode('utf-8')
    df = pd.read_csv(StringIO(content), names=dk_lut.label, header=None)
    df.index = df.columns

    return df
