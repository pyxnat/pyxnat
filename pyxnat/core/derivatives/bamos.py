import os
import nibabel as nib
import tempfile
import numpy as np
import pandas as pd

XNAT_RESOURCE_NAME = 'BAMOS'

BAMOS_LABELS = {0: 'background',
                1: 'left frontal',
                2: 'right frontal',
                3: 'left parietal',
                4: 'right parietal',
                5: 'left occipital',
                6: 'right occipital',
                7: 'left temporal',
                8: 'right temporal',
                9: 'basal ganglia',
                10: 'infratentorial'}


def volume(self):
    """ Returns the estimated volume of the identified lesions (i.e. voxels
    with a value higher than 0.5."""

    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    f = list(self.files('CorrectLesion_*nii.gz'))[0]
    f.get(fp)
    d = nib.load(fp)
    size = np.prod(d.header['pixdim'].tolist()[:4])
    n = np.array(d.dataobj)
    v = np.sum(n[n >= 0.5]) * size
    os.remove(fp)
    return v


def n_lesions(self):
    """ Returns the estimated number of lesions i.e. the # of found connected
    components in Connect_WS3WT3WC1Lesion*_corr.nii.gz. """

    fd, fp = tempfile.mkstemp(suffix='.nii.gz')
    os.close(fd)

    f = list(self.files('Connect_WS3WT3WC1Lesion_*_corr.nii.gz'))[0]
    f.get(fp)
    d = nib.load(fp)
    n = len(np.unique(d.dataobj))

    os.remove(fp)
    return n


def stats(self):
    """ Collects descriptive statistics based on the segmented lesions of the
    white matter, including volumes and number of lesions. A voxel is
    considered as a part of a lesion if it has a value higher than 0.5."""
    def _download_data_(self):
        fd, fp = tempfile.mkstemp(suffix='.nii.gz')
        os.close(fd)

        f = list(self.files('Connect_WS3WT3WC1Lesion_*_corr.nii.gz'))[0]
        f.get(fp)
        cc = np.array(nib.load(fp).dataobj)
        f = list(self.files('CorrectLesion_*nii.gz'))[0]
        f.get(fp)
        d = nib.load(fp)
        size = np.prod(d.header['pixdim'].tolist()[:4])
        les = np.array(d.dataobj)

        f = list(self.files('Layers_*.nii.gz'))[0]
        f.get(fp)
        d1 = np.array(nib.load(fp).dataobj)

        f = list(self.files('Lobes_*.nii.gz'))[0]
        f.get(fp)
        d2 = np.array(nib.load(fp).dataobj)
        os.remove(fp)
        return cc, d1, d2, les, size

    def _roistats_from_map(m, atlas1, atlas2, func=np.mean):
        import itertools
        assert(m.shape == atlas1.shape)
        assert(m.shape == atlas2.shape)
        labels1 = list(np.unique(atlas1))
        labels2 = list(np.unique(atlas2))

        combinations = list(itertools.product(labels1, labels2))

        mask = lambda i1, i2: (atlas1 == i1) & (atlas2 == i2)
        label_values = dict([((i1, BAMOS_LABELS[i2]), func(m[mask(i1, i2)]))
                             for (i1, i2) in combinations])
        return label_values


    cc, d1, d2, les, size = _download_data_(self)
    d1[d1 == 5] = 4  # Merging layer 5 with layer 4

    stats1 = _roistats_from_map(cc, d1, d2, func=lambda d: len(np.unique(d)))
    stats2 = _roistats_from_map(les, d1, d2, func=lambda d: np.sum(d[d >= 0.5]))

    df = [(d, r, val, stats2[(d, r)] * size) for (d, r), val in stats1.items()]
    df = pd.DataFrame(df, columns=['depth', 'region', 'n', 'volume'])

    return df


def bullseye_plot(self, ax=None, figsize=(12, 8), segBold=[],
                  measurement='volume', stats=None, cm=None):
    """
    Bullseye's representation of cerebral white matter hyperintensities
    (adapted from https://matplotlib.org/stable/gallery/specialty_plots/leftventricle_bulleye.html)

    Args:
    `ax`          If None then a new Matplotlib figure is created
    `figsize`     Figure size
    `segBold`     Highlight some sections (if an integer is passed then will
                   highlight the regions over the given nth percentile)
    `measurement` Measurement to plot (default: `volume`)
    `stats`       Can be used to plot precalculated stats. (default: None -
                   stats will be calculated for the current resource)
    `cm`          Color map (default: `matplotlib.pyplot.cm.YlOrRd`)

    Reference:
    C. Sudre et al., J Neuroradiol, 2018
    """
    from matplotlib import pyplot as plt
    import matplotlib as mpl

    num = 80   # sampling parameter
    nreg = 10  # how many regions
    ndep = 4   # how many layers
    offset = 18 * np.pi/180  # in radians
    ordered_labels = [3, 1, 2, 4, 8, 6, 10, 9, 5, 7]

    def _ravel_stats_(stats, measurement='n'):
        data = []
        for d in range(1, ndep+1):
            for label in ordered_labels:
                q = 'depth == %s & region == "%s"' % (d, BAMOS_LABELS[label])
                v = float(stats.query(q)[measurement])
                data.append(v)
        return data

    if stats is None:
        stats = self.stats()

    layers = [int(e) for e in set(stats['depth'])][1:]  # remove 0 (background)

    # Highlight regions > nth percentile
    if isinstance(segBold, int):
        pc = stats[measurement].quantile(q=segBold/100.0)
        segBold = []
        for _, r in stats.query('%s > @pc' % measurement).iterrows():
            label = [k for (k, v) in BAMOS_LABELS.items() if v == r.region][0]
            idx = ordered_labels.index(label)
            segBold.append((int(r.depth)-1, idx))

    data = _ravel_stats_(stats, measurement=measurement)

    # Start plotting
    data = np.array(data).ravel()
    vlim = [data.min(), data.max()]
    if cm is None:
        cm = plt.cm.YlOrRd

    axnone = ax is None
    if axnone:
        fig, ax = plt.subplots(subplot_kw=dict(projection='polar'),
                               figsize=figsize)

    theta = np.linspace(0, 2*np.pi, num*nreg)
    r = np.linspace(0.2, 1, ndep+1)

    # Draw circles
    linewidth = 1
    for i in range(r.shape[0]):
        ax.plot(theta, np.repeat(r[i], theta.shape), '-k', lw=linewidth)

    # Draw lines
    for i in range(nreg):
        theta_i = (i * 360.0/nreg) * np.pi/180 + offset
        ax.plot([theta_i, theta_i], [r[0], 1], '-k', lw=linewidth)

    # Paint areas
    for depth in range(ndep):
        r0 = r[depth:depth+2]
        r0 = np.repeat(r0[:, np.newaxis], num, axis=1).T
        for i in range(nreg):
            theta0 = theta[i*num:(i+1)*num] + offset
            theta0 = np.repeat(theta0[:, np.newaxis], 2, axis=1)
            z = np.ones((num, 2)) * data[depth*nreg + i]
            ax.pcolormesh(theta0, r0, z, vmin=vlim[0], vmax=vlim[1], cmap=cm)

            # Highlight some regions
            if (depth, i) in segBold:
                ax.plot(theta0, r0, '-k', lw=linewidth+2)
                ax.plot(theta0[0], [r[depth], r[depth+1]], '-k', lw=linewidth+1)
                ax.plot(theta0[-1], [r[depth], r[depth+1]], '-k', lw=linewidth+1)

    ax.set_ylim([0, 1])
    ax.set_yticklabels(layers)

    thetaticks = np.arange(0, 360, 36)
    ordered_labels = [7, 3, 1, 2, 4, 8, 6, 10, 9, 5]

    labels = [BAMOS_LABELS[e] for e in ordered_labels]
    ax.set_thetagrids(thetaticks, labels=labels)
    ax.tick_params(pad=12, labelsize=14, axis='both')
    bbox = dict(boxstyle="round", ec="white", fc="white", alpha=0.5)
    plt.setp(ax.get_xticklabels(), bbox=bbox)

    if axnone:  # Add legend
        cNorm = mpl.colors.Normalize(vmin=vlim[0], vmax=vlim[1])

        ax = fig.add_axes([0.3, 0.04, 0.45, 0.05])
        ticks = [vlim[0], 0, vlim[1]]
        cb = mpl.colorbar.ColorbarBase(ax, cmap=cm, norm=cNorm,
                                       orientation='horizontal', ticks=ticks)
    plt.show()

    if axnone:
        return fig, ax
