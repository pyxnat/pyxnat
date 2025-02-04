from .pet_fdg import quantification_results as _qr
from .pet_fdg import regional_quantification as _rq

XNAT_RESOURCE_NAMES = ['FTM_QUANTIFICATION', 'FTM_QUANTIFICATION2']


def quantification_results(self):
    return _qr(self)


def centiloids(self, optimized=False):
    df = self.quantification_results()
    q = 'region == "cortex" &'\
        'atlas.isna() & reference_region == "whole_cerebellum" &'\
        ' measurement == "centiloid"'

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    return float(df.query(q)['value'].iloc[0])


def regional_quantification(self, optimized=True, reference_region='whole_cerebellum',
                            atlas='hammers'):
    return _rq(self, optimized, reference_region, atlas)
