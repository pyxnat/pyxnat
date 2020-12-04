from .pet_fdg import quantification_results as qr

XNAT_RESOURCE_NAME = 'FTM_QUANTIFICATION'


def quantification_results(self):
    return qr(self)


def centiloids(self, optimized=True):
    df = self.quantification_results()
    q = 'region == "cortex" &'\
        'atlas.isna() & reference_region == "whole_cerebellum" &'\
        ' measurement == "centiloid"'

    q += ' & %soptimized_pet' % {True: '', False: '~'}[optimized]
    return float(df.query(q)['value'])
