#!/usr/bin/env python
# encoding: utf-8
#
# bpt.py
#
# Created by José Sánchez-Gallego on 19 Jan 2017.


from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import matplotlib.pyplot as plt
import numpy as np

from mpl_toolkits.axes_grid1 import ImageGrid


def get_snr(snr_min, emission_line, default=3):
    """Convenience function to get the minimum SNR for a certain emission line.

    If ``snr_min`` is a dictionary and ``emision_line`` is one of the keys,
    returns that value. If the emission line is not included in the dictionary,
    returns ``default``. If ``snr_min`` is a float, returns that value
    regardless of the ``emission_line``.

    """

    if not isinstance(snr_min, dict):
        return snr_min

    if emission_line in snr_min:
        return snr_min[emission_line]
    else:
        return default


def get_masked(maps, emline, snr=1):
    """Convenience function to get masked arrays without negative values."""

    gflux = maps['emline_gflux_' + emline]
    gflux_masked = gflux.masked

    # Masks spaxels with flux <= 0
    gflux_masked.mask |= (gflux_masked.data <= 0)

    # Masks all spaxels that don't reach the cutoff SNR
    gflux_masked.mask |= gflux.snr < snr
    gflux_masked.mask |= gflux.ivar == 0

    return gflux_masked


def _get_kewley06_axes(use_oi=True):
    """Creates custom axes for displaying Kewley06 plots."""

    fig = plt.figure(1, (8.5, 10))
    fig.clf()

    plt.subplots_adjust(top=0.99, bottom=0.08, hspace=0.01)

    # The axes for the three classification plots
    grid_bpt = ImageGrid(fig, 211,
                         nrows_ncols=(1, 3) if use_oi else (1, 2),
                         direction='row',
                         axes_pad=0.1,
                         add_all=True,
                         label_mode='L',
                         share_all=False)

    # The axes for the galaxy display
    gal_bpt = ImageGrid(fig, 212, nrows_ncols=(1, 1))

    # Plots the classification boundary lines
    xx_sf_nii = np.linspace(-1.281, 0.045, int(1e4))
    xx_sf_sii = np.linspace(-2, 0.315, int(1e4))
    xx_sf_oi = np.linspace(-2.5, -0.7, int(1e4))

    xx_comp_nii = np.linspace(-2, 0.4, int(1e4))

    xx_agn_sii = np.array([-0.308, 1.0])
    xx_agn_oi = np.array([-1.12, 0.5])

    grid_bpt[0].plot(xx_sf_nii, kewley_sf_nii(xx_sf_nii), 'k--', zorder=90)
    grid_bpt[1].plot(xx_sf_sii, kewley_sf_sii(xx_sf_sii), 'r-', zorder=90)
    if use_oi:
        grid_bpt[2].plot(xx_sf_oi, kewley_sf_oi(xx_sf_oi), 'r-', zorder=90)

    grid_bpt[0].plot(xx_comp_nii, kewley_comp_nii(xx_comp_nii), 'r-', zorder=90)

    grid_bpt[1].plot(xx_agn_sii, kewley_agn_sii(xx_agn_sii), 'b-', zorder=80)
    if use_oi:
        grid_bpt[2].plot(xx_agn_oi, kewley_agn_oi(xx_agn_oi), 'b-', zorder=80)

    # Adds captions
    grid_bpt[0].text(-1, -0.5, 'SF', ha='center', fontsize=12, zorder=100, color='c')
    grid_bpt[0].text(0.5, 0.5, 'AGN', ha='left', fontsize=12, zorder=100)
    grid_bpt[0].text(-0.08, -1.2, 'Comp', ha='left', fontsize=12, zorder=100, color='g')

    grid_bpt[1].text(-1.2, -0.5, 'SF', ha='center', fontsize=12, zorder=100)
    grid_bpt[1].text(-1, 1.2, 'Seyfert', ha='left', fontsize=12, zorder=100, color='r')
    grid_bpt[1].text(0.3, -1, 'LINER', ha='left', fontsize=12, zorder=100, color='m')

    if use_oi:
        grid_bpt[2].text(-2, -0.5, 'SF', ha='center', fontsize=12, zorder=100)
        grid_bpt[2].text(-1.5, 1, 'Seyfert', ha='left', fontsize=12, zorder=100)
        grid_bpt[2].text(-0.1, -1, 'LINER', ha='right', fontsize=12, zorder=100)

    # Sets the ticks, ticklabels, and other details
    xtick_limits = ((-2, 1), (-1.5, 1), (-2.5, 0.5))
    axes = [0, 1, 2] if use_oi else [0, 1]

    for ii in axes:

        grid_bpt[ii].get_xaxis().set_tick_params(direction='in')
        grid_bpt[ii].get_yaxis().set_tick_params(direction='in')

        grid_bpt[ii].set_xticks(np.arange(xtick_limits[ii][0], xtick_limits[ii][1] + 0.5, 0.5))
        grid_bpt[ii].set_xticks(np.arange(xtick_limits[ii][0],
                                          xtick_limits[ii][1] + 0.1, 0.1), minor=True)
        grid_bpt[ii].set_yticks(np.arange(-1.5, 2.0, 0.5))
        grid_bpt[ii].set_yticks(np.arange(-1.5, 1.6, 0.1), minor=True)

        grid_bpt[ii].grid(which='minor', alpha=0.2)
        grid_bpt[ii].grid(which='major', alpha=0.5)

        grid_bpt[ii].set_xlim(xtick_limits[ii][0], xtick_limits[ii][1])

        grid_bpt[ii].set_ylim(-1.5, 1.6)
        if use_oi:
            grid_bpt[ii].set_ylim(-1.5, 1.8)

        grid_bpt[ii].spines['top'].set_visible(True)

        if ii in [0, 1]:
            if not use_oi and ii == 1:
                continue
            grid_bpt[ii].get_xticklabels()[-1].set_visible(False)

    grid_bpt[0].set_ylabel(r'log([OIII]/H$\beta$)')

    grid_bpt[0].set_xlabel(r'log([NII]/H$\alpha$)')
    grid_bpt[1].set_xlabel(r'log([SII]/H$\alpha$)')
    if use_oi:
        grid_bpt[2].set_xlabel(r'log([OI]/H$\alpha$)')

    gal_bpt[0].grid(False)

    return fig, grid_bpt, gal_bpt[0]


def kewley_sf_nii(log_nii_ha):
    """Star forming classification line for log([NII]/Ha)."""
    return 0.61 / (log_nii_ha - 0.05) + 1.3


def kewley_sf_sii(log_sii_ha):
    """Star forming classification line for log([SII]/Ha)."""
    return 0.72 / (log_sii_ha - 0.32) + 1.3


def kewley_sf_oi(log_oi_ha):
    """Star forming classification line for log([OI]/Ha)."""
    return 0.73 / (log_oi_ha + 0.59) + 1.33


def kewley_comp_nii(log_nii_ha):
    """Composite classification line for log([NII]/Ha)."""
    return 0.61 / (log_nii_ha - 0.47) + 1.19


def kewley_agn_sii(log_sii_ha):
    """Seyfert/LINER classification line for log([SII]/Ha)."""
    return 1.89 * log_sii_ha + 0.76


def kewley_agn_oi(log_oi_ha):
    """Seyfert/LINER classification line for log([OI]/Ha)."""
    return 1.18 * log_oi_ha + 1.30


def bpt_kewley06(maps, snr=3, return_figure=True, use_oi=True):
    """Returns ionisation regions, making use of the boundaries defined in Kewley+06.

    Makes use of the classification system defined by
    `Kewley et al. (2006) <https://ui.adsabs.harvard.edu/#abs/2006MNRAS.372..961K/abstract>`_
    to return classification masks for different ionisation mechanisms. If ``return_figure=True``,
    produces and returns a matplotlib figure with the classification plots (based on
    Kewley+06 Fig. 4) and the 2D spatial distribution of classified spaxels (i.e., a map of the
    galaxy in which each spaxel is colour-coded based on its emission mechanism).

    While it is possible to call this function directly, its normal use will be via the
    :func:`~marvin.tools.maps.Maps.get_bpt` method.

    Parameters:
        maps (a Marvin :class:`~marvin.tools.maps.Maps` object)
            The Marvin Maps object that contains the emission line maps to be used to determine
            the BPT classification.
        snr (float or dict):
            The signal-to-noise cutoff value for the emission lines used to generate the BPT
            diagram. If ``snr`` is a single value, that signal-to-noise will be used for all
            the lines. Alternatively, a dictionary of signal-to-noise values, with the
            emission line channels as keys, can be used.
            E.g., ``snr={'ha': 5, 'nii': 3, 'oi': 1}``. If some values are not provided,
            they will default to ``SNR>=3``.
        return_figure (bool):
            If ``True``, it also returns the matplotlib figure_ of the BPT diagram plot,
            which can be used to modify the style of the plot.
        use_oi (bool):
            If ``True``, uses the OI diagnostic line during BPT spaxel classification

    Returns:
        bpt_return:
            ``bpt_kewley06`` always returns a dictionary of sets of classification masks. The
            classification masks (not to be confused with bitmasks) are boolean arrays with the
            same shape as the Maps or Cube (without the spectral dimension) that can be used
            to select spaxels belonging to a certain excitation process (e.g., star forming).
            The sets of masks are labeled as ``'nii'`` (for the constraints in the diagram
            NII/Halpha vs OIII/Hbeta), ``'sii'`` (SII/Halpha vs OIII/Hbeta), ``'oi'`` (OI/Halpha
            vs OIII/Hbeta, only if ``use_oi=True``), and ``'global'``, which applies all the
            previous constraints at once. Each set is a dictionary of masks, labeled as ``'sf'``
            (star forming), ``'comp'`` (composite), ``'agn'``, ``'seyfert'``, ``'liner'``,
            ``'invalid'`` (spaxels that are masked out in at least one of the emission
            line maps used), and ``'ambiguous'`` (spaxels that do not fall in any classification or
            fall in more than one). The ``'ambiguous'`` mask is only available for the ``'global'``
            set, while the ``'comp'`` mask is only available for ``'nii'``. ``'seyfert'`` and
            ``'liner'`` are not available for ``'nii'``. All the masks are unique (a spaxel can
            only belong to one of them) with the exception of ``'agn'``, which intersects with
            ``'seyfert'`` and ``'liner'``. If ``return_figure=True``, ``get_bpt`` will return a
            tuple, the first elemnt of which is the dictionary of classification masks, and the
            second the matplotlib figure.

    Example:
        >>> maps_8485_1901 = Maps(plateifu='8485-1901')
        >>> bpt_masks = bpt_kewley06(maps_8485_1901)

        Gets the global mask for star forming spaxels

        >>> sf = bpt_masks['global']['sf']

        Gets the seyfert mask based only on the SII/Halpha vs OIII/Hbeta diagnostics

        >>> seyfert_sii = bpt_masks['sii']['seyfert']

    """

    # Gets the necessary emission line maps
    oiii = get_masked(maps, 'oiii_5008', snr=get_snr(snr, 'oiii'))
    nii = get_masked(maps, 'nii_6585', snr=get_snr(snr, 'nii'))
    ha = get_masked(maps, 'ha_6564', snr=get_snr(snr, 'ha'))
    hb = get_masked(maps, 'hb_4862', snr=get_snr(snr, 'hb'))
    sii = get_masked(maps, 'sii_6718', snr=get_snr(snr, 'sii'))
    oi = get_masked(maps, 'oi_6302', snr=get_snr(snr, 'oi'))

    # Calculate masked logarithms
    log_oiii_hb = np.ma.log10(oiii / hb)
    log_nii_ha = np.ma.log10(nii / ha)
    log_sii_ha = np.ma.log10(sii / ha)
    log_oi_ha = np.ma.log10(oi / ha)

    # Calculates masks for each emission mechanism according to the paper boundaries.
    # The log_nii_ha < 0.05, log_sii_ha < 0.32, etc are necessary because the classification lines
    # diverge and we only want the region before the asymptota.
    sf_mask_nii = ((log_oiii_hb < kewley_sf_nii(log_nii_ha)) & (log_nii_ha < 0.05)).filled(False)
    sf_mask_sii = ((log_oiii_hb < kewley_sf_sii(log_sii_ha)) & (log_sii_ha < 0.32)).filled(False)
    sf_mask_oi = ((log_oiii_hb < kewley_sf_oi(log_oi_ha)) & (log_oi_ha < -0.59)).filled(False)
    sf_mask = sf_mask_nii & sf_mask_sii & sf_mask_oi if use_oi else sf_mask_nii & sf_mask_sii

    comp_mask = ((log_oiii_hb > kewley_sf_nii(log_nii_ha)) & (log_nii_ha < 0.05)).filled(False) & \
                ((log_oiii_hb < kewley_comp_nii(log_nii_ha)) & (log_nii_ha < 0.465)).filled(False)

    agn_mask_nii = ((log_oiii_hb > kewley_comp_nii(log_nii_ha)) |
                    (log_nii_ha > 0.465)).filled(False)
    agn_mask_sii = ((log_oiii_hb > kewley_sf_sii(log_sii_ha)) |
                    (log_sii_ha > 0.32)).filled(False)
    agn_mask_oi = ((log_oiii_hb > kewley_sf_oi(log_oi_ha)) |
                   (log_oi_ha > -0.59)).filled(False)
    agn_mask = agn_mask_nii & agn_mask_sii & agn_mask_oi if use_oi else agn_mask_nii & agn_mask_sii

    seyfert_mask_sii = agn_mask & (kewley_agn_sii(log_sii_ha) < log_oiii_hb).filled(False)
    seyfert_mask_oi = agn_mask & (kewley_agn_oi(log_oi_ha) < log_oiii_hb).filled(False)
    seyfert_mask = seyfert_mask_sii & seyfert_mask_oi if use_oi else seyfert_mask_sii

    liner_mask_sii = agn_mask & (kewley_agn_sii(log_sii_ha) > log_oiii_hb).filled(False)
    liner_mask_oi = agn_mask & (kewley_agn_oi(log_oi_ha) > log_oiii_hb).filled(False)
    liner_mask = liner_mask_sii & liner_mask_oi if use_oi else liner_mask_sii

    # The invalid mask is the combination of spaxels that are invalid in all of the emission maps
    invalid_mask = ha.mask | oiii.mask | nii.mask | hb.mask | sii.mask
    if use_oi:
        invalid_mask |= oi.mask

    # The ambiguous mask are spaxels that are not invalid but don't fall into any of the
    # emission mechanism classifications.
    ambiguous_mask = ~(sf_mask | comp_mask | seyfert_mask | liner_mask) & ~invalid_mask

    bpt_nii_classification = {'sf': sf_mask_nii,
                              'comp': comp_mask,
                              'agn': agn_mask_nii,
                              'invalid': invalid_mask}

    bpt_sii_classification = {'sf': sf_mask_sii,
                              'agn': agn_mask_sii,
                              'seyfert': seyfert_mask_sii,
                              'liner': liner_mask_sii,
                              'invalid': invalid_mask}

    bpt_oi_classification = {'sf': sf_mask_oi,
                             'agn': agn_mask_oi,
                             'seyfert': seyfert_mask_oi,
                             'liner': liner_mask_oi,
                             'invalid': invalid_mask}

    bpt_global_classification = {'sf': sf_mask,
                                 'comp': comp_mask,
                                 'agn': agn_mask,
                                 'seyfert': seyfert_mask,
                                 'liner': liner_mask,
                                 'invalid': invalid_mask,
                                 'ambiguous': ambiguous_mask}

    bpt_return_classification = {'global': bpt_global_classification,
                                 'nii': bpt_nii_classification,
                                 'sii': bpt_sii_classification}
    if use_oi:
        bpt_return_classification['oi'] = bpt_oi_classification

    if not return_figure:
        return bpt_return_classification

    # Does all the plotting
    fig, grid_bpt, gal_bpt = _get_kewley06_axes(use_oi=use_oi)

    sf_kwargs = {'marker': 's', 's': 12, 'color': 'c', 'zorder': 50, 'alpha': 0.7, 'lw': 0.0}
    sf_handler = grid_bpt[0].scatter(log_nii_ha[sf_mask], log_oiii_hb[sf_mask], **sf_kwargs)
    grid_bpt[1].scatter(log_sii_ha[sf_mask], log_oiii_hb[sf_mask], **sf_kwargs)

    comp_kwargs = {'marker': 's', 's': 12, 'color': 'g', 'zorder': 45, 'alpha': 0.7, 'lw': 0.0}
    comp_handler = grid_bpt[0].scatter(log_nii_ha[comp_mask], log_oiii_hb[comp_mask],
                                       **comp_kwargs)
    grid_bpt[1].scatter(log_sii_ha[comp_mask], log_oiii_hb[comp_mask], **comp_kwargs)

    seyfert_kwargs = {'marker': 's', 's': 12, 'color': 'r', 'zorder': 40, 'alpha': 0.7, 'lw': 0.0}
    seyfert_handler = grid_bpt[0].scatter(log_nii_ha[seyfert_mask], log_oiii_hb[seyfert_mask],
                                          **seyfert_kwargs)
    grid_bpt[1].scatter(log_sii_ha[seyfert_mask], log_oiii_hb[seyfert_mask], **seyfert_kwargs)

    liner_kwargs = {'marker': 's', 's': 12, 'color': 'm', 'zorder': 35, 'alpha': 0.7, 'lw': 0.0}
    liner_handler = grid_bpt[0].scatter(log_nii_ha[liner_mask], log_oiii_hb[liner_mask],
                                        **liner_kwargs)
    grid_bpt[1].scatter(log_sii_ha[liner_mask], log_oiii_hb[liner_mask], **liner_kwargs)

    amb_kwargs = {'marker': 's', 's': 12, 'color': '0.6', 'zorder': 30, 'alpha': 0.7, 'lw': 0.0}
    amb_handler = grid_bpt[0].scatter(log_nii_ha[ambiguous_mask], log_oiii_hb[ambiguous_mask],
                                      **amb_kwargs)
    grid_bpt[1].scatter(log_sii_ha[ambiguous_mask], log_oiii_hb[ambiguous_mask], **amb_kwargs)

    if use_oi:
        grid_bpt[2].scatter(log_oi_ha[sf_mask], log_oiii_hb[sf_mask], **sf_kwargs)
        grid_bpt[2].scatter(log_oi_ha[comp_mask], log_oiii_hb[comp_mask], **comp_kwargs)
        grid_bpt[2].scatter(log_oi_ha[seyfert_mask], log_oiii_hb[seyfert_mask], **seyfert_kwargs)
        grid_bpt[2].scatter(log_oi_ha[liner_mask], log_oiii_hb[liner_mask], **liner_kwargs)
        grid_bpt[2].scatter(log_oi_ha[ambiguous_mask], log_oiii_hb[ambiguous_mask], **amb_kwargs)

    # Creates the legend
    grid_bpt[0].legend([sf_handler, comp_handler, seyfert_handler, liner_handler, amb_handler],
                       ['Star-forming', 'Composite', 'Seyfert', 'LINER', 'Ambiguous'], ncol=2,
                       loc='upper left', frameon=True, labelspacing=0.1, columnspacing=0.1,
                       handletextpad=0.1, fontsize=9)

    # Creates a RGB image of the galaxy, and sets the colours of the spaxels to match the
    # classification masks
    gal_rgb = np.zeros((ha.shape[0], ha.shape[1], 3), dtype=np.uint8)

    for ii in [1, 2]:  # Cyan
        gal_rgb[:, :, ii][sf_mask] = 255

    gal_rgb[:, :, 1][comp_mask] = 128  # Green

    gal_rgb[:, :, 0][seyfert_mask] = 255  # Red

    # Magenta
    gal_rgb[:, :, 0][liner_mask] = 255
    gal_rgb[:, :, 2][liner_mask] = 255

    for ii in [0, 1, 2]:
        gal_rgb[:, :, ii][invalid_mask] = 255  # White
        gal_rgb[:, :, ii][ambiguous_mask] = 169  # Grey

    # Shows the image.
    gal_bpt.imshow(gal_rgb, origin='lower', aspect='auto', interpolation='nearest')

    gal_bpt.set_xlim(0, ha.shape[1] - 1)
    gal_bpt.set_ylim(0, ha.shape[0] - 1)
    gal_bpt.set_xlabel('x [spaxels]')
    gal_bpt.set_ylabel('y [spaxels]')

    return (bpt_return_classification, fig)
