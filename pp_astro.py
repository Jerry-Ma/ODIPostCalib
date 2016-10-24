#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-10-17 22:20
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
pp_astro.py
"""


import os
from extern.apus.utils import get_main_config
from extern.apus.utils import default_to_main_config
from extern.apus.utils import tlist_wrapper
import glob


@default_to_main_config
def tlist(dummy, inreg):
    inflag = 'masked'
    inglob = 'masked_*odi_?.fits'
    # goodflag = 'linked'
    goodglob = 'linked_*odi_?.fits'
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
    if conf.scamp_config['ASTREF_CATALOG'] == 'FILE':
        t30_follows = [t13, t21]
        t30_extras = t21['out']
    # tries to make use of the saved catalog
    else:
        t30_follows = t13
        t30_extras = glob.glob(os.path.join(
            conf.confdir, '{0}_*_r*.cat'.format(
                conf.scamp_config['ASTREF_CATALOG'])))
        if len(t30_extras) > 0:
            t30_extras = os.path.abspath(
                    sorted(t30_extras, key=os.path.getctime)[-1])
            conf.scamp_config['ASTREF_CATALOG'] = 'FILE'
    t30 = dict(
            name='scamp',
            func='scamp',
            pipe='collate',
            in_=(goodglob, inreg),
            add_inputs='scamp_%s_{id[0]}_{name[0]}'
            '_odi_{band[0]}.fits' % (inflag),
            extras=t30_extras,
            in_keys=[('dummy', 'in'), 'ASTREFCAT_NAME'],
            params=dict(conf.scamp_config, **{
                'MERGEDOUTCAT_NAME': os.path.join(conf.confdir, 'merged.cat'),
                'MERGEDOUTCAT_TYPE': 'FITS_LDAC',
                'REFOUT_CATPATH': conf.confdir,
                'HEADER_SUFFIX': '.hdr_astro',
                'WRITE_XML': 'Y',
                'XML_NAME': os.path.join(conf.jobdir, 'scamp.xml'),
                }),
            follows=t30_follows
            )
    t31 = dict(
            name='create swarp header',
            func='python -u recipes/create_swarp_header.py {in} {out}',
            pipe='transform',
            in_=(goodglob, inreg),
            replace_inputs=[
                'scamp_%s_{id[0]}_{name[0]}_odi_{band[0]}'
                '.hdr_astro' % (inflag),
                'scamp_%s_{id[0]}_{name[0]}_odi_{band[0]}'
                '.hdr_astro' % (inflag),
                ],
            out='{basename[0]}.hdr_swarp',
            follows=t30,
            )
    t32 = dict(
            name='plot dist stability',
            func='python -u recipes/plot_distortion.py {in} {out} 1',
            in_=t31,
            pipe='merge',
            out='fig_scamp_distortion.eps'
            )
    return tlist_wrapper([
        t10, t11, t12, t13,
        t20, t21,
        t30, t31, t32
        ], goodglob, inreg)
