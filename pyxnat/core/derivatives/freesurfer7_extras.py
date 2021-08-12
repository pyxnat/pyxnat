XNAT_RESOURCE_NAMES = ['FREESURFER7_EXTRAS']


def brainstem_substructures_volumes(self):
    """Returns brainstem substructures volumetry as estimated by the FreeSurfer
    brainstem segmentation module."""
    import pandas as pd

    table = []
    f = list(self.files('*brainstemSsVolumes.v*.txt'))[0]
    uri = f._uri

    res = self._intf.get(uri).text.split('\n')
    d1 = dict([each.split(' ') for each in res[:-1]])
    d2 = dict([('%s' % k, float(v))
              for k, v in d1.items()])

    for region, value in d2.items():
        row = [region, value]
        table.append(row)

    columns = ['region', 'value']
    return pd.DataFrame(table, columns=columns)


def thalamic_nuclei_volumes(self):
    """Returns thalamic nuclei volumetry as estimated by the FreeSurfer thalamus
    segmentation  module."""
    import pandas as pd

    table = []
    f = list(self.files('*ThalamicNuclei.v*.T1.volumes.txt'))[0]
    uri = f._uri

    res = self._intf.get(uri).text.split('\n')
    d1 = dict([each.split(' ') for each in res[:-1]])
    d2 = dict([('%s' % k, float(v))
              for k, v in d1.items()])

    for label, value in d2.items():
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
    f = list(self.files('*hypothalamic_subunits_volumes.v*.csv'))[0]
    uri = f._uri

    res = self._intf.get(uri).text.split('\n')
    csv_content = list(csv.reader(res, delimiter=','))
    d1 = dict(zip(csv_content[0], csv_content[1]))
    d2 = dict([('%s' % k, float(v))
               for k, v in d1.items()
               if k != 'subject'])

    for label, value in d2.items():
        side, region = label.split(' ', 1)
        if side == 'whole':
            region, side = label.split(' ', 1)

        row = [side, region, value]
        table.append(row)

    columns = ['side', 'region', 'value']
    return pd.DataFrame(table, columns=columns)
