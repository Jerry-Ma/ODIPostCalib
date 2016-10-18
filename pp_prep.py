#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-07-30 20:04
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
pp_prep.py
"""


import os
from extern.apus.utils import get_main_config
from extern.apus.utils import default_to_main_config
from extern.apus.utils import tlist_wrapper
from recipes.apply_ota_mask import check_if_uptodate


@default_to_main_config
def tlist(inglob, inreg):
    conf = get_main_config()
    # generate sky layout files
    t1 = dict(
            name='get sky layout',
            func='python -u recipes/get_sky_layout.py {in} {out}',
            pipe='collate',
            in_=(inglob, inreg),
            out=['sky_{name[0]}.asc',
                 'sky_{name[0]}.reg',
                 'sky_{name[0]}.wcs'],
            )
    # get GSC catalog for bright star mask
    sky_reg = r'sky_(?P<name>.+)\.asc'
    t2 = dict(
            name='get bright star catalog',
            func='python -u recipes/get_gsc.py {0} {{in}} {{out}}'.format(
                conf.bright_star_mag),
            pipe='transform',
            in_=('sky_*.asc', sky_reg),
            out='gsc_{name[0]}.cat',
            follows=t1,
            )
    # get SDSS catalog for calib
    t3 = dict(
            name='get sdss catalog',
            func='python -u recipes/get_sdss.py {0} {{in}} {{out}}'.format(
                conf.band),
            pipe='transform',
            in_=('sky_*.asc', sky_reg),
            out='sdss_{name[0]}.cat',
            follows=t1,
            )
    # merge catalogs for different target
    t4 = dict(
            name='merge catalogs',
            func='python -u recipes/merge_catalogs.py {in} {out}',
            pipe='collate',
            in_=[(t2, r'(?P<kind>sdss|gsc)_.+\.cat'),
                 (t3, r'(?P<kind>sdss|gsc)_.+\.cat')],
            out='{kind[0]}.cat',
            )
    # looking for info in the flag file and create masked images
    t5 = dict(
            name='apply ota mask',
            func='python -u recipes/apply_ota_mask.py {in} {out}',
            pipe='transform',
            extras=os.path.abspath(conf.ota_flag_file),
            in_=(inglob, inreg),
            out='masked_{id[0]}_{name[0]}_odi_{band[0]}.fits',
            check_if_uptodate=check_if_uptodate,
            )
    return tlist_wrapper([t1, t2, t3, t4, t5], 'masked_*.fits', inreg)
