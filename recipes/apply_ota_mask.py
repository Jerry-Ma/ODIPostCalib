#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-07-30 23:04
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
apply_ota_mask.py
"""


import os
import re
import numpy as np
from multiprocessing import Pool
from multiprocessing import cpu_count
from common import open_with_meta
from common import get_image_flag


def apply_bpmask(data, otaxy, layout):
    if layout == 'odi56':
        bpmdir = 'extern/bpm/odi_5x6'
    elif layout == 'podi':
        bpmdir = 'extern/bpm/podi/'
    else:
        raise RuntimeError('focal plane layout {0} not recognized'
                           .format(layout))
    bpm_file = os.path.join(bpmdir, 'bpm_xy{0}.reg'.format(otaxy))
    bpm = []
    with open(bpm_file, 'r') as fo:
        for ln in fo.readlines():
            rect = re.match(r'box\(([0-9+-., ]+)\)', ln.strip())
            if rect is not None:
                rect = map(float, rect.group(1).split(','))
                # print "box from bpm: {0}".format(rect)
                bpm.append((
                    rect[0] - rect[2] * 0.5,
                    rect[0] + rect[2] * 0.5,
                    rect[1] - rect[3] * 0.5,
                    rect[1] + rect[3] * 0.5))
            else:
                continue
    for box in bpm:
        l, r, b, t = [int(v + 0.5) for v in box]
        data[b:t, l:r] = np.nan
    return data


if __name__ == "__main__":

    import sys

    in_file, flag_file, out_file = sys.argv[1:]
    if os.path.exists(flag_file):
        print "use flag file: {0}".format(flag_file)
    else:
        print "create empty flag file: {0}".format(flag_file)
        with open(flag_file, 'a'):
            os.utime(flag_file, None)
    otas = get_image_flag(in_file, flag_file)
    # for now ignore -1 flag, which will be handled by link_images.py
    otas = [i for i in otas if i != -1]
    print 'mask:', otas
    hdulist, exts, layout = open_with_meta(in_file)
    print "focal plane layout: {0}".format(layout)

    def mp_worker(args):
        data, otaxy = args
        print "working on OTA {0}".format(otaxy)
        if otaxy in otas:
            data[:, :] = np.nan
        else:
            data = apply_bpmask(data, otaxy, layout)
        return data

    pool = Pool(cpu_count())
    ret = pool.map_async(
            mp_worker,
            [(hdulist[i].data, otaxy) for i, otaxy in exts]
            ).get(9999999)
    for ii, (i, _) in enumerate(exts):
        hdulist[i].data = ret[ii]
    hdulist.writeto(out_file, clobber=True)
