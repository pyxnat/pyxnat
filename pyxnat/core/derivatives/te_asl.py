from . import basil

XNAT_RESOURCE_NAMES = ['TE_ASL']


def perfusion(self):
    """Perfusion and arrival-time mean values"""
    return basil.perfusion(self)


def stats(self):
    """Regional perfusion and arrival-time statistics.

    Parses `oxford_asl` region-analysis CSV outputs for whole-brain (global),
    GM and WM perfusion and arrival-time summaries based on the Harvard-Oxford
    cortical and subcortical atlases.
    """
    import csv
    import pandas as pd

    stats_files = {'whole_brain_perfusion': 'region_analysis.csv',
                   'GM_perfusion': 'region_analysis_gm.csv',
                   'WM_perfusion': 'region_analysis_wm.csv',
                   'whole_brain_arrival': 'region_analysis_arrival.csv',
                   'GM_arrival': 'region_analysis_arrival_gm.csv',
                   'WM_arrival': 'region_analysis_arrival_wm.csv'}
    region_stats = []
    columns = []
    for roi, fn in stats_files.items():
        f = self.files(f'*{fn}')[0]
        content = self._intf.get(f.attributes()['URI']).text.splitlines()
        for idx, row in enumerate(csv.reader(content)):
            if idx == 0:
                columns = ['region_analysis'] + row
            else:
                region_stats.append([roi] + row)

    df = pd.DataFrame(region_stats, columns=columns)
    numeric_cols = ['Nvoxels', 'Mean', 'Std', 'Median',
                    'IQR', 'Precision-weighted mean', 'I2']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    return df
