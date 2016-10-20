#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-07-31 09:57
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
common.py
"""


import os
import glob
from astropy.io import fits
from extern.pyjerry.instrument import wiyn
import numpy as np
from multiprocessing import Pool
from multiprocessing import cpu_count


def open_with_meta(in_file):
    hdulist = fits.open(in_file)
    instru = hdulist[0].header.get('INSTRUME', '5odi')
    if instru == '5odi':
        layout = 'odi56'
        get_ota_xy = wiyn.WIYNFact.get_ota_xy
        maxhdu = 99
    elif instru == 'podi':
        layout = 'podi'
        get_ota_xy = wiyn.WIYNFact.get_ota_xy_podi
        maxhdu = 10  # work around techdata extension
    else:
        raise RuntimeError("instrument {0} not recognized".format(instru))
    exts = [(i, get_ota_xy(i)) for i, h in enumerate(hdulist[:maxhdu])
            if isinstance(h, fits.ImageHDU)]
    return hdulist, exts, layout


def mp_worker_combine_odi(args):
    data, (_, otaxy), scalefunc, combfunc = args
    print "working on OTA {0}".format(otaxy)
    ret = np.dstack([scalefunc(d) for d in data])
    ret = combfunc(ret)
    for d in data:
        del d
    return ret
    # return combfunc(np.dstack([scalefunc(d) for d in data]))


def combine_odi(in_files, combfunc, scalefunc, exts=None, jobs=1):
    if exts is None:
        hdulist, exts, _ = open_with_meta(in_files[0])
        hdulist.close()
    images = []
    for fname in in_files:
        print "read image {0}".format(fname)
        images.append(fits.open(fname, memmap=True))
    ret = []
    if jobs == 1:
        for ext, otaxy in exts:
            print "working on OTA {0}".format(otaxy)
            data = np.dstack([scalefunc(h[ext].data) for h in images])
            data = combfunc(data)
            ret.append(data)
            for h in images:
                del h[ext].data
        for image in images:
            image.close()
    else:
        datacube = [[h[ext].data for h in images] for ext, otaxy in exts]
        pool = Pool(cpu_count())
        ret = pool.map_async(
                mp_worker_combine_odi,
                zip(datacube, exts,
                    [scalefunc, ] * len(exts),
                    [combfunc, ] * len(exts)),
                ).get(9999999)
    return ret


def get_image_flag(in_file, flag_file):
    chips = []
    with open(flag_file, 'r') as fo:
        for ln in fo.readlines():
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            ln = ln.split('#', 1)[0].strip().split()  # remove in line comment
            if len(ln) < 2:
                continue
            else:
                if ln[0] == '*':
                    chips.extend(map(int, ln[1:]))
                else:
                    match = [f for f in glob.glob(ln[0])
                             if os.path.samefile(f, in_file)]
                    if len(match) == 1:
                        if ln[1] == '*':
                            chips.append(-1)
                        else:
                            chips.extend(map(int, ln[1:]))
                        break
                    elif len(match) == 0:
                        continue
                    else:
                        raise RuntimeError('unable to get image flag for {0}'
                                           .format(in_file))
    return list(set(chips))
