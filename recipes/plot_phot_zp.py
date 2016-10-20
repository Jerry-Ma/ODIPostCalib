#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-08-05 12:19
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
plot_phot_zp.py
"""

from __future__ import division
import numpy as np

from extern.pyjerry.mympl import SolarizedColor as sc
from extern.pyjerry.mympl import TexStyle as ts
from extern.pyjerry import mympl
from scipy.stats import sigmaclip


def plot_zp_color(ax, bulk, ck):
    bulk = bulk[(bulk[ck['smag']] > ck['smaglims'][0]) &
                (bulk[ck['smag']] < ck['smaglims'][1])]
    color = bulk[ck['cmag1']] - bulk[ck['cmag2']]
    zp = bulk[ck['smag']] - bulk[ck['mag']] - ck['zp'] - ck['kins'] * color
    zp0 = np.median(zp)
    # 1mag clip
    # bulk = bulk[(zp < zp0 + 1) & (zp > zp0 - 1)]
    # zp = zp[(zp < zp0 + 1) & (zp > zp0 - 1)]
    print "median residue", np.median(zp)
    # if ck['scflag'] == 'oditool':
    #     print "adjust zp level for odi-tools"
    #     zp = zp - zp0
    zperr = np.hypot(bulk[ck['semag']], bulk[ck['emag']])
    clipped, lo, up = sigmaclip(zp, ck['clip'], ck['clip'])
    im = (zp < up) & (zp > lo)
    ex = ~im & (zp > zp0 - 1) & (zp < zp0 + 1)
    ax.set_xlim((-0.5, 4))
    ax.set_ylim((-0.7, 1.))

    pltkw = dict(ms=6, fmt='o')
    pltkw = dict(fmt='o', ms=3, capsize=0, mew=0)
    pltkw_ex = dict(fmt='D', ms=2, capsize=0, mew=1, fillstyle='none')
    legs = []
    if np.any(im):
        leg = ax.errorbar(color[im], zp[im], yerr=zperr[im], **pltkw)
        for lc in leg[2]:
            ecolor = lc.get_color()[0]
            eecolor = sc.hsv(ecolor, s=0.2, v=0.9)
            lc.set_color(eecolor)
        legs.append((leg, ts.tt('clipped')))
        if np.any(ex):
            legex = ax.errorbar(color[ex], zp[ex], yerr=zperr[ex],
                                color=eecolor, **pltkw_ex)
            for lc in legex[2]:
                lc.set_color(eecolor)
    ax.axhline(0.05 * np.log10(np.e) * 2.5, ls='--', color=sc.base02)
    ax.axhline(-0.05 * np.log10(np.e) * 2.5, ls='--', color=sc.base02)
    ax.text(-0.1, 0.0, ts.tt(r'\pm 5\%'),
            verticalalignment='center', fontsize=20)
    label = [
            r'n_{obj}=%d' % (len(zp[im | ex])),
            r'{\Delta}res.=%.5f' % (np.std(zp[im | ex])),
            r'n_{obj,clip}=%d' % (len(zp[im])),
            r'{\Delta}res._{clip}=%.5f' % (np.std(zp[im]))
            ]
    ax.text(0.05, 0.92, ts.tt('\n'.join(label)),
            transform=ax.transAxes,
            verticalalignment='top')


def get_simple_zp(bulk, ck):
    # fit a linear line to get color term
    subbulk = bulk[(bulk[ck['smag']] > ck['smaglims'][0]) &
                   (bulk[ck['smag']] < ck['smaglims'][1])]
    color = subbulk[ck['cmag1']] - subbulk[ck['cmag2']]
    zp = subbulk[ck['smag']] - subbulk[ck['mag']]
    err = np.hypot(subbulk[ck['semag']], subbulk[ck['emag']])
    fit = np.polyfit(color, zp, 1, w=1 / err)
    return fit[0], fit[1]


if __name__ == '__main__':

    import sys
    from astropy.table import Table
    # import glob
    import os

    band, maglim_lo, maglim_up, cat_file, out_name = sys.argv[1:-1]
    cat = Table.read(cat_file, format='ascii.commented_header')
    plotid = os.path.splitext(os.path.basename(cat_file))[0]
    # print "default color term: {0}".format(kins)
    cband = {'u': ('u', 'g'),
             'g': ('g', 'r'),
             'r': ('r', 'i'),
             'i': ('r', 'i'),
             'z': ('i', 'z'),
             }
    ck = {
        'smag': band,
        'semag': 'err_{0}'.format(band),
        'smaglims': (float(maglim_lo), float(maglim_up)),
        'mag': 'MAG_AUTO',
        'emag': 'MAGERR_AUTO',
        # 'mag': 'MAG_APER_3',
        # 'emag': 'MAGERR_APER_3',
        'plotid': plotid,
        'band': band,
        'cband': cband[band],
        'cmag1': cband[band][0],
        'cmag2': cband[band][1],
        'clip': 3.0,
        }
    kins, zp = get_simple_zp(cat, ck)
    print "phot eqn: mag_sdss = {0:.3f} * color_sdss" \
          " + {1:.3f} + mag_ins".format(kins, zp)
    ck['kins'] = kins
    ck['zp'] = zp

    canvas = mympl.CanvasOne(
        width=800,
        aspect=0.618,
        scale=1,
        usetw=False,
        )
    fig, (ax, ) = canvas.parts()
    plot_zp_color(ax, cat, ck)

    canvas.save_or_show(out_name,
                        bbox_inches='tight',
                        # pad_inches=0,
                        )
