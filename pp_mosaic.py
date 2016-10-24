#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-10-18 20:25
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
pp_mosaic.py
"""


# import os
from extern.apus.utils import get_main_config
from extern.apus.utils import default_to_main_config
from extern.apus.utils import tlist_wrapper


@default_to_main_config
def tlist(inglob, inreg):
    # here inglob is linked_*.fits
    # do per object swarp
    conf = get_main_config()
    swarpreg = (r'(?P<prefix>[^_/]+)_'
                r'(?P<calflag>[^_/]+)_'
                r'(?P<imflag>[^_/]+)_'  # (?P<id>20\d{6}T\d{6}\.\d)_'
                r'(?P<name>[^/]+)_'
                r'odi_(?P<band>\w)\.(?P<ext>.+)')
    t10 = dict(
            name='swarp with astro',
            func='swarp',
            pipe='collate',
            in_=(conf.tlist[-1], inreg),
            add_inputs='{imflag[0]}_{id[0]}_'
            '{name[0]}_odi_{band[0]}.fits',
            in_keys=[('dummy', 'in'), ],
            out=['swarp_astro_{imflag[0]}_'  # {id[0]}_'
                 '{name[0]}_odi_{band[0]}.fits',
                 'coadd_astro_{imflag[0]}_'  # {id[0]}_'
                 '{name[0]}_odi_{band[0]}.wht.fits'],
            params=dict(conf.swarp_config,
                        HEADER_SUFFIX='.hdr_swarp',
                        XML_NAME='swarp_with_astro.xml',
                        ),
            )
    t11 = dict(
            name='swarp without astro',
            func='swarp',
            pipe='collate',
            in_=(inglob, inreg),
            add_inputs='{imflag[0]}_{id[0]}_'
            '{name[0]}_odi_{band[0]}.fits',
            in_keys=[('dummy', 'in'), ],
            out=['swarp_qr_{imflag[0]}_'  # {id[0]}_'
                 '{name[0]}_odi_{band[0]}.fits',
                 'coadd_qr_{imflag[0]}_'  # {id[0]}_'
                 '{name[0]}_odi_{band[0]}.wht.fits'],
            params=dict(conf.swarp_config,
                        HEADER_SUFFIX='.none',
                        XML_NAME='swarp_without_astro.xml',
                        ),
            )
    t2 = dict(
            name='fix nan pixel',
            func='extern/apus/scripts/apply_mask.py {in} {out}',
            pipe='transform',
            in_=([t10, t11], swarpreg),
            out='coadd_{calflag[0]}_{imflag[0]}_'  # {id[0]}_
            '{name[0]}_odi_{band[0]}.fits'
            )
    return tlist_wrapper([
        t10, t11,
        t2,
        ], 'coadd_*odi_?.fits', swarpreg)
