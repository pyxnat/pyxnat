XNAT_RESOURCE_NAME = 'ASHS'

def volumes(self, mode='corr_nogray'):
    import pandas as pd

    f = list(self.files('*icv.txt'))[0]
    uri = f._uri
    res = self._intf.get(uri).text.split(' ')

    f = list(self.files('*_left_%s_volumes.txt'%mode))[0]
    uri = f._uri
    resl = self._intf.get(uri).text.split('\n')

    f = list(self.files('*_right_%s_volumes.txt'%mode))[0]
    uri = f._uri
    resr = self._intf.get(uri).text.split('\n')

    table = []
    for resx in [resl, resr]:
        for line in resx:
                if line == '':
                    continue
                line = line.split(' ')
                s = line[0]
                side = line[1]
                region = line[2]
                i = int(line[-2])
                m = float(line[-1])
                table.append([s, side, region, i, m])

    table.append([res[0], None, 'tiv', None, float(res[1].rstrip('\n'))])

    columns = ['subject', 'side', 'region', 'n_slices', 'volume']
    return pd.DataFrame(table, columns=columns)
