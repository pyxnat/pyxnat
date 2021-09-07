XNAT_RESOURCE_NAMES = ['FREESURFER7_EXTRAS']


def __extract_volumes(self, filename):
    f = list(self.files(filename))[0]
    uri = f._uri

    res = self._intf.get(uri).text.split('\n')
    if filename.endswith('.csv'):
        import csv
        csv_content = list(csv.reader(res, delimiter=','))
        d1 = dict(zip(csv_content[0], csv_content[1]))
    else:
        d1 = dict([each.split(' ') for each in res[:-1]])

    return dict([('%s' % k, float(v))
                 for k, v in d1.items()
                 if k != 'subject'])


def brainstem_substructures_volumes(self):
    """Returns brainstem substructures volumetry as estimated by the FreeSurfer
    brainstem segmentation module."""
    import pandas as pd

    table = []
    data = __extract_volumes(self, '*brainstemSsVolumes.v*.txt')
    for region, value in data.items():
        row = [region, value]
        table.append(row)

    columns = ['region', 'value']
    return pd.DataFrame(table, columns=columns)


def thalamic_nuclei_volumes(self):
    """Returns thalamic nuclei volumetry as estimated by the FreeSurfer thalamus
    segmentation  module."""
    import pandas as pd

    table = []
    data = __extract_volumes(self, '*ThalamicNuclei.v*.T1.volumes.txt')
    for label, value in data.items():
        side, region = label.split('-', 1)
        row = [side.lower(), region, value]
        table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)


def hypothalamic_subunits_volumes(self):
    """Returns hypothalamic subunits volumetry as estimated by the FreeSurfer
    hypothalamus segmentation module."""
    import pandas as pd
    import csv

    table = []
    data = __extract_volumes(self, '*hypothalamic_subunits_volumes.v*.csv')
    for label, value in data.items():
        side, region = label.split(' ', 1)
        if side == 'whole':
            region, side = label.split(' ', 1)

        row = [side, region, value]
        table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)
