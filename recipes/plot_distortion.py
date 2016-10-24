#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-10-21 13:50
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
plot_distortion.py
"""

from __future__ import division
# import numpy as np

# from extern.pyjerry.mympl import SolarizedColor as sc
from extern.pyjerry.mympl import TexStyle as ts
from extern.pyjerry import mympl
from extern.pyjerry.instrument import wiyn

from astropy.io import fits
from matplotlib import gridspec
# import matplotlib


keys = ['CRPIX1', 'CRPIX2', 'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2',
        'PV1_0', 'PV1_1', 'PV1_2', 'PV1_3', 'PV1_4', 'PV1_5',
        'PV1_6', 'PV1_7', 'PV1_8', 'PV1_9', 'PV1_10',
        'PV2_0', 'PV2_1', 'PV2_2', 'PV2_3', 'PV2_4', 'PV2_5',
        'PV2_6', 'PV2_7', 'PV2_8', 'PV2_9', 'PV2_10',
        ]

var_keys = [
        'CD1_1', 'CD1_2', 'CD2_1', 'CD2_2', 'CRPIX1', 'CRPIX2',
        'PV1_0', 'PV1_1', 'PV1_2',
        'PV2_0', 'PV2_1', 'PV2_2',
        ]


def get_fp(hdrs):

    data = [[] for _ in keys]
    # in_files.sort(key=lambda s: s[-11:])
    for hdr in hdrs:
        head = fits.Header.fromstring(hdr, sep='\n')
        for i, key in enumerate(keys):
            defval = 1 if key == 'PV1_1' or key == 'PV2_1' else 0
            data[i].append(head.get(key, defval))
    return data


def get_hdr_list(hdrfile):
    hdrs = []
    hdr = []
    with open(hdrfile, 'r') as fo:
        for ln in fo.readlines():
            hdr.append(ln)
            if ln.rstrip('\n') == 'END     ':
                hdrs.append(''.join(hdr))
                hdr = []
    return hdrs


if __name__ == '__main__':

    import sys
    import os
    in_files = sys.argv[1:-2]
    out_file = sys.argv[-2]

    bulk = []
    fid = []
    for hdrfile in in_files:
        bulk.append(get_hdr_list(hdrfile))
        fid.append(os.path.splitext(os.path.basename(hdrfile))[0])
    # merge same extension
    bulk = zip(*bulk)
    print "number of extensions: {0}".format(len(bulk))
    nrow = 6
    ncol = 5

    mympl.use_hc_color('kelly')
    canvas = mympl.CanvasOne(
        width=1000,
        aspect=1,
        scale=1,
        usetw=True,
        )
    fig, (dummy, ) = canvas.parts()
    canvas.let_dummy(dummy, tick=False)
    gs0 = gridspec.GridSpec(nrow, ncol + 1, wspace=0.25, hspace=0.25)
    lx = fig.add_subplot(gs0[:, ncol])
    canvas.let_dummy(lx, tick=False)
    x = range(len(in_files))
    bxes = []
    yoff = 0.00005
    for h, hdrs in enumerate(bulk):
        data = get_fp(hdrs)
        otaxy = wiyn.WIYNFact.get_ota_xy(h + 1)
        otax = int(str(otaxy)[0]) - 1
        otay = int(str(otaxy)[1]) - 1
        bxes.append(fig.add_subplot(gs0[nrow - otay - 1, otax]))
        # bxes[-1].set_yscale('log')
        bxes[-1].set_ylim((1 - yoff, 1 + yoff))
        bxes[-1].set_yticks([1 - yoff, 1, 1 + yoff])
        bxes[-1].ticklabel_format(style='sci', scilimits=(0, 0),
                                  axis='y', useOffset=False)
        # bxes[-1].get_yaxis().set_major_formatter(
        #     matplotlib.ticker.ScalarFormatter())
        for key, y in zip(keys, data):
            y0 = y[0]
            # y = [abs(i / y0) if y0 != 0 else 1 for i in y]
            y = [abs(i / y0) if y0 != 0 else 1 for i in y]
            marker = 'x' if key in var_keys else 'o'
            ls = ':' if key in var_keys else '--'
            bxes[-1].plot(x, y, ls=ls, marker=marker, label=ts.tt(key),
                          mew=1, ms=4, fillstyle='none')
            bxes[-1].text(
                    0.05, 0.05, "OTA {0}".format(otaxy),
                    verticalalignment='bottom', horizontalalignment='left',
                    transform=bxes[-1].transAxes)
    legs, lbls = bxes[0].get_legend_handles_labels()
    lx.legend(legs, lbls, loc='upper left')
    canvas.save_or_show(out_file,
                        bbox_inches='tight',
                        # pad_inches=0,
                        )
