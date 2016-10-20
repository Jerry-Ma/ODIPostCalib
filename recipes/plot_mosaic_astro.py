#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-08-23 14:53
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
plot_astro_vec.py
"""

from __future__ import division
import numpy as np

from extern.pyjerry.mympl import SolarizedColor as sc
from extern.pyjerry.mympl import TexStyle as ts
from extern.pyjerry import mympl

from matplotlib.patches import Ellipse
import matplotlib
from astropy.wcs import WCS
import matplotlib.cm as cm
from astropy.table import Table


def plot_vec(ax, ra1, dec1, ra2, dec2, x, y, a, b, t, f, ps):
    tr_tan = ax.get_transform("world")
    dra = (ra2 - ra1) * np.cos((dec1 + dec2) * 0.5 * np.pi / 180.) * 3600.
    ddec = (dec2 - dec1) * 3600.
    pa = np.arctan2(dra, ddec) * 180. / np.pi
    leg = ax.quiver(
            ra1, dec1, dra, ddec, pa,
            pivot='tail', cmap=cm.rainbow, clim=(-180., 180.),
            units='xy', angles='xy',
            scale_units='xy', scale=1. / 3600. / 0.2 / 2,
            color=sc.red,
            transform=tr_tan,
            width=25,
            )
    # plot fwhm and ellipticity as ellipse
    # scale = 15
    # ells = [Ellipse(
    #     xy=(x[i], y[i]),
    #     width=f[i] * a[i] / b[i] * scale,
    #     height=f[i] * scale,
    #     angle=t[i], fill=False, lw=0.1)
    #     for i in range(len(x))]
    # cmap = matplotlib.cm.get_cmap('rainbow')
    # cnorm = matplotlib.colors.Normalize(vmin=3, vmax=1.5 / ps)
    # for i, e in enumerate(ells):
    #     ax.add_artist(e)
    #     e.set_clip_box(ax.bbox)
    #     e.set_edgecolor(cmap(cnorm(f[i])))
    # eleg = Ellipse(xy=(1000, 250),
    #                width=2. / ps * scale,
    #                height=1. / ps * scale,
    #                angle=0, fill=False, lw=1.0)
    # eleg.set_clip_box(ax.bbox)
    # eleg.set_edgecolor(cmap(cnorm(1 / ps)))
    # ax.add_artist(eleg)
    # leg = ax.quiver(
    #         [218.75, ], [35.25, ], 0.5, 0, 0.6,
    #         pivot='tail', cmap=cm.rainbow, clim=(0, 0.6),
    #         units='xy', angles='xy',
    #         scale_units='xy', scale=1. / 3600 / ps,
    #         color=sc.red,
    #         transform=tr_tan,
    #         )
    ax.quiverkey(leg, 0.50, 0.05, 1,
                 ts.tt('0.5^{\prime\prime}'),
                 coordinates='axes',
                 )
    # ax.scatter([0, 1000], [0, 1000])


if __name__ == '__main__':

    import sys
    from astropy.io import fits

    band, ps, cat_file, fits_file, out_file = sys.argv[1:-1]
    cat = Table.read(cat_file, format='ascii.commented_header')

    hdulist = fits.open(fits_file)
    exts = [(0, 1), ]
    w = []
    for ext, chip in exts:
        w.append(WCS(hdulist[ext]))

    canvas = mympl.CanvasN(
        width=600,
        aspect=1,
        scale=1,
        usetw=False,
        ngrid=len(exts),
        # tile=cfht.get_chip_layout(),
        projection=w,
        hide_inner_tick='xy',
        )
    fig, axes = canvas.parts()
    ax, bxes = axes[0], axes[1:]
    for i, (ext, chip) in enumerate(exts):
        bx = bxes[i]
        hdu = hdulist[ext]
        bx.set_aspect('equal')
        bx.set_xlim(-0.5, hdu.data.shape[1] - 0.5)
        bx.set_ylim(-0.5, hdu.data.shape[0] - 0.5)
        bx.coords[0].display_minor_ticks(True)
        bx.coords[1].display_minor_ticks(True)
        bx.coords[0].set_ticklabel_visible(canvas.xtickvis[i])
        bx.coords[1].set_ticklabel_visible(canvas.ytickvis[i])
        subcat = cat[cat['EXT_NUMBER'] == chip]
        plot_vec(
            bx, subcat['ALPHA_J2000'], subcat['DELTA_J2000'],
            subcat['ra'], subcat['dec'],
            subcat['X_IMAGE'], subcat['Y_IMAGE'],
            subcat['A_IMAGE'], subcat['B_IMAGE'], subcat['THETA_IMAGE'],
            subcat['FWHM_IMAGE'],
            float(ps),
            ),
    # ax.set_xlim((bbox[0], bbox[1]))
    # ax.set_ylim((bbox[2], bbox[3]))
    # ax.set_xlim((200, 240))
    # ax.set_ylim((30, 40))
    canvas.save_or_show(out_file,
                        bbox_inches='tight',
                        # pad_inches=0,
                        )
