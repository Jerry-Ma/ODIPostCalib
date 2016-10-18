#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-10-17 22:20
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
pp_astro.py
"""


# import os
from extern.apus.utils import get_main_config
from extern.apus.utils import default_to_main_config
from extern.apus.utils import tlist_wrapper


@default_to_main_config
def tlist(inglob, inreg):
    # inglob = 'masked_*.fits'
    conf = get_main_config()
    t10 = dict(
            name='sex for astrometry',
            func='sex',
            pipe='transform',
            in_=(inglob, inreg),
            out='astro_{imflag[0]}_{id[0]}_{name[0]}_odi_{band[0]}.fits',
            params=dict(
                CATALOG_TYPE='FITS_LDAC',
                DETECT_MINAREA=5,
                DETECT_THRESH=10.0,
                ),
            # follows=conf.tlist[-1]
            )
    t11 = dict(
            name='astro ldac to cat',
            func='./extern/apus/scripts/ldac_to_asc.sh {in} {out}',
            pipe='transform',
            in_=(t10, inreg),
            out='{basename[0]}.cat',
            )
    t12 = dict(
            name='clean up astro cat',
            func='python -u recipes/clean_up_catalog.py {0} {{in}} {{out}}'
            .format(conf.band),
            pipe='transform',
            in_=(t11, inreg),
            extras='gsc.cat',  # output of task 'merge catalog'
            out='astroclean_{imflag[0]}_{id[0]}_{name[0]}_odi_{band[0]}.asc',
            follows='merge catalogs',
            )
    t13 = dict(
            name='create scamp cat',
            func='python -u extern/apus/scripts/ldac_replace.py'
            ' {in} {out}',
            pipe='transform',
            in_=(t10, inreg),
            add_inputs='astroclean_{imflag[0]}_{id[0]}_{name[0]}'
            '_odi_{band[0]}.asc',
            out='scamp_{imflag[0]}_{id[0]}_{name[0]}_odi_{band[0]}.fits',
            follows=t12,
            )
    t20 = dict(
            name='get scamp refcat wcs',
            func='python -u recipes/get_scamp_wcs.py {in} {out}',
            pipe='merge',
            in_=[inglob, 'sdss.cat'],
            out='sdss.wcs',
            follows='merge catalogs'
            )
    t21 = dict(
            name='create scamp refcat',
            func='extern/apus/scripts/create_refcat.py '
            '{0} {1} {2} {{in}} {{out}}'.format(conf.band,
                                                *conf.calib_mag_range),
            pipe='transform',
            in_='sdss.cat',
            add_inputs=t20,
            out='scamp_sdss.fits',
            follows='merge catalogs',
            )
    t30 = dict(
            name='scamp',
            func='scamp',
            pipe='collate',
            in_=(inglob, inreg),
            add_inputs='scamp_{imflag[0]}_{id[0]}_{name[0]}'
            '_odi_{band[0]}.fits',
            # u band perseus
            extras=t21['out'],
            # extras=[os.path.abspath('./2MASS_0319+4131_r40.cat'), ],
            # extras=[os.path.abspath('./SDSS-R9_0319+4131_r35.cat'), ],
            in_keys=[('dummy', 'in'), 'ASTREFCAT_NAME'],
            # in_keys=[('dummy', 'in'), ],
            params={
                # 'ASTREF_CATALOG': '2MASS',
                # 'ASTREF_CATALOG': 'SDSS-R9',
                'ASTREF_CATALOG': 'FILE',
                'SOLVE_PHOTOM': 'N',
                'AHEADER_GLOBAL': 'extern/z03_1.ahead',
                'HEADER_SUFFIX': '.hdr_astro',
                # 'MOSAIC_TYPE': 'UNCHANGED',
                # 'MOSAIC_TYPE': 'LOOSE',
                # 'MOSAIC_TYPE': 'FIX_FOCALPLANE',
                'MOSAIC_TYPE': 'SAME_CRVAL',
                # 'HEADER_TYPE': 'FOCAL_PLANE',
                'DISTORT_DEGREES': 3,
                'POSANGLE_MAXERR': 1.0,
                'POSITION_MAXERR': 5.0,
                'CHECKPLOT_RES': 2048,
                'CROSSID_RADIUS': 1.2,
                'MAGZERO_OUT': 25,
                'MERGEDOUTCAT_NAME': 'merged.cat',
                'MERGEDOUTCAT_TYPE': 'FITS_LDAC',
                # 'ASTREFCENT_KEYS': 'ALPHA_J2000,DELTA_J2000'
                # 'VERBOSE_TYPE': 'FULL'
                },
            follows=[t13, t21],
            )
    return tlist_wrapper([
        t10, t11, t12, t13,
        t20, t21,
        t30,
        ], inglob, inreg)
