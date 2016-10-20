#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-07-31 15:46
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
pp_photometry.py

perform photometry and generate diagnostic plots
"""


from extern.apus.utils import default_to_main_config
from extern.apus.utils import tlist_wrapper
from apus.utils import get_main_config


@default_to_main_config
def tlist(inglob, inreg):
    conf = get_main_config()
    t1 = dict(
            name='mosaic photometry',
            func='sex',
            pipe='transform',
            in_=(inglob, inreg),
            add_inputs='{basename[0]}.wht.fits',
            in_keys=[('in', 'WEIGHT_IMAGE'), ],
            out='photsex_{basename[0]}.cat',
            dry_run=False,
            params={'CATALOG_TYPE': 'ASCII_HEAD',
                    'DETECT_MINAREA': 3,
                    'DETECT_THRESH': 1.5,
                    'ANALYSIS_THRESH': 1.5,
                    'DEBLEND_MINCONT': 0.005,
                    'PHOT_APERTURES': [18, 27, 36, 45, 54, 72, 90, 109],
                    'BACK_SIZE': 64,
                    'WEIGHT_TYPE': 'MAP_WEIGHT',
                    # 'WEIGHT_TYPE': 'NONE',
                    'WEIGHT_GAIN': 'Y',
                    'GAIN_KEY': 'GAIN',
                    # 'GAIN': 1.23,
                    'MAG_ZEROPOINT': 25,
                    },
            outparams=['MAG_APER(8)', 'MAGERR_APER(8)',
                       'FLUX_MAX',
                       'AWIN_IMAGE', 'BWIN_IMAGE', 'ELONGATION'
                       ],
            )
    t2 = dict(
            name='mosaic cat to ascii',
            func='extern/apus/scripts/sex_to_ascii.py {in} {out}',
            pipe='transform',
            in_=t1,
            out='{basename[0]}.asc',
            )
    t3 = dict(
            name='match mosaic to sdss',
            func='./recipes/match_to_sdss.sh {in} {out}',
            pipe='transform',
            in_=t2,
            extras='sdss.cat',
            out='sdss{basename[0]}.asc',
            follows='merge catalogs',
            )
    t4 = dict(
            name='plot zp residue',
            func='python -u recipes/plot_phot_zp.py'
            ' {0} {1} {2} {{in}} {{out}} 1'.format(
                conf.band, *conf.calib_mag_range),
            pipe='transform',
            in_=t3,
            out='fig_{basename[0]}_zp.eps',
            )
    t5 = dict(
            name='plot astrometry vector',
            func='python -u recipes/plot_mosaic_astro.py'
            ' {0} {1} {{in}} {{out}} 1'.format(
                conf.band, conf.swarp_config['PIXEL_SCALE']),
            pipe='transform',
            in_=(t3, r'(?P<prefix>[^_/]+)_(?P<name>[^/]+)\.asc'),
            add_inputs='{name[0]}.fits',
            out='fig_{basename[0]}_astro.eps',
            )

    return tlist_wrapper([
        t1, t2, t3, t4, t5
        ], inglob, inreg)
