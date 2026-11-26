XNAT_RESOURCE_NAMES = ['SAMSEG_T1', 'SAMSEG_FLAIR', 'SAMSEG_T1FLAIR']


def _read_samseg_stats(self, filename):
    """Read a SAMSEG stats file from the resource and return (region, value, units) tuples."""

    files = [f for f in self.files(f'*{filename}')
             if f._uri.rsplit('/', 1)[-1] == filename]
    if not files:
        raise FileNotFoundError(f'{filename} not found in {self}')
    if len(files) > 1:
        raise ValueError(f'Multiple {filename} files in {self}')

    uri = files[0]._uri
    response = self._intf.get(uri)
    response.raise_for_status()

    rows = []
    prefix = '# Measure '
    for line in response.text.splitlines():
        if line.startswith(prefix):
            region, value, units = line[len(prefix):].split(',')
            rows.append((region.strip(), float(value), units.strip()))

    if not rows:
        raise ValueError(f'No measurements in {uri}')

    return rows


def stats(self):
    """Return SAMSEG regional volumes and sbTIV as a pandas DataFrame."""

    import pandas as pd

    cols = ['region', 'value', 'units', 'source']

    rows = [(region, value, units, 'samseg.stats')
            for region, value, units
            in _read_samseg_stats(self, 'samseg.stats')]
    regional = pd.DataFrame(rows, columns=cols)
    return pd.concat([regional, self.sbtiv()], ignore_index=True)


def sbtiv(self):
    """Return the SAMSEG intracranial volume in mm³ as a one-row DataFrame."""

    import pandas as pd

    cols = ['region', 'value', 'units', 'source']

    rows = _read_samseg_stats(self, 'sbtiv.stats')
    if len(rows) != 1:
        raise ValueError(f'Expected one measurement in sbtiv.stats in {self}')

    region, value, units = rows[0]
    if region != 'Intra-Cranial':
        raise ValueError(f'Expected an Intra-Cranial measurement in {self}')

    return pd.DataFrame([(region, value, units, 'sbtiv.stats')], columns=cols)