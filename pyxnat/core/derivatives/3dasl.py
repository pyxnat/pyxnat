from .basil import volumes as vols

XNAT_RESOURCE_NAMES = ['3DASL_QUANTIFICATION']


def volumes(self):
    """Partial volume segmentations for CSF, GM, WM (fsl_anat)"""
    return vols(self)


def perfusion(self):
    """Perfusion mean values and summary statistics"""
    import pandas as pd
    from io import StringIO

    f = self.file('quantification_results.csv')
    content = self._intf.get(f.attributes()['URI']).content.decode('utf-8')
    df = pd.read_csv(StringIO(content))
    return df
