from .pet_fdg import quantification_results as qr

XNAT_RESOURCE_NAME = 'FTM_QUANTIFICATION2'


def quantification_results(self):
    return qr(self)


def centiloids(self, optimized=False):
    df = self.quantification_results()
    q = 'region == "cortex" &'\
        'atlas.isna() & reference_region == "whole_cerebellum" &'\
        ' measurement == "centiloid"'

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    return float(df.query(q)['value'])


def regional_quantification(self, optimized=True, 
                            reference_region='whole_cerebellum', atlas='hammers'):
    df = self.quantification_results()

    q = 'reference_region == "{reference_region}" &'\
        ' measurement == "suvr"'.format(reference_region=reference_region)

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    df = df.query(q)
    df = df.query(f'atlas == "{atlas}"', engine='python')
    
    assert(len(set(df['atlas'])) == 1)
    assert(len(set(df['optimized_pet'])) == 1)

    return df
