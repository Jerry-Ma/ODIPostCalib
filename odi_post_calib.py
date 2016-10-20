#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-07-30 19:35
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
odi_post_calib.py

This is the entry point of the apus pipeline
for post-QR calibration of WIYN ODI data

"""

import os
import pp_prep
import pp_astro
import pp_mosaic
import pp_photometry
from extern.apus import core
from extern.apus.utils import get_main_config


# ### basic config
# name for the dataset; will be used as the name of your work directory
runkey = 'demo_data'

# band of the dataset; will be used for photometry calibration
band = 'u'

# tunable parameters
bright_star_mag = 15  # used for remove bright sources using GSC
calib_mag_range = (18, 21)  # used for select calibration sources

# location and format of the original data; its content will be sym-linked to
# the work dir
# e.g.: input_root = '/home/foo/yourodidatafolder/calibrated'
input_root = 'demo_data/calibrated'

# glob pattern for the data to be linked
# the following will select all fits files in input_root, with given band
input_glob = '20??????T*/*odi_{0}.????.fits'.format(band)

# regex for parse the input filename; used for creating more readable symlinked
# filenames; no need to change
input_reg = (r'.+(?P<id>20\d{6}T\d{6}\.\d)_(?P<name>\w+)_odi_(?P<band>\w)'
             r'\.(?P<qr>\d{4})/.+\.fits')


# scamp config
# used for generating scamp configuration on the fly
# generated config file is in jobdir/config/conf.scamp
scamp_config = {
    # ### clean sdss catalog using sql query adapted from Ralf QR
    'ASTREF_CATALOG': 'FILE',
    # ### SCAMP built-in SDSS
    # 'ASTREF_CATALOG': 'SDSS-R9',
    # ### SCAMP built-in 2MASS
    # 'ASTREF_CATALOG': '2MASS',
    'AHEADER_GLOBAL': 'extern/z03_1.ahead',
    'MOSAIC_TYPE': 'SAME_CRVAL',
    # 'HEADER_TYPE': 'FOCAL_PLANE',
    'DISTORT_DEGREES': 3,
    'POSANGLE_MAXERR': 1.0,
    'POSITION_MAXERR': 5.0,
    'CHECKPLOT_RES': 2048,
    'CROSSID_RADIUS': 1.2,
    'SOLVE_PHOTOM': 'Y',
    'MAGZERO_OUT': 25,
    }

# swarp config
# used for generating swarp configuration on the fly
# generated config file is in jobdir/config/conf.swarp
swarp_config = {
    'PIXELSCALE_TYPE': 'MANUAL',
    'PIXEL_SCALE': 0.20,
    'HEADER_SUFFIX': '.none',  # to be overridden
    'FSCALE_DEFAULT': 99,  # for rejecting failed phot calib image
    'BACK_SIZE': 64,
    'DELETE_TMPFILES': 'Y',
    }

# ### end of basic config


# ### advanced config
# generate jobkeys and work dir layouts; no need to change
conf = get_main_config()
conf.jobkey = '_'.join([runkey, band])
conf.jobdir = os.path.join(band, runkey)
conf.confdir = os.path.join(conf.jobdir, 'config')
conf.logdir = 'logs'
conf.task_io_default_dir = conf.jobdir
conf.bright_star_mag = bright_star_mag
conf.calib_mag_range = calib_mag_range

# refer to readme for more explanations on path_prefix
conf.env_overrides = {
        # this is to let apus know where the astromatic softwares are
        'path_prefix': 'extern/astromatic',
        # this is to store the .resamp file
        'scratch_dir': conf.jobdir,
        }

# for masking OTA per image; this should be a text file with the following
# optional contents for blacklisting files:
#    *          51       # mask OTA 51 for all file
#    foo1.fits   *       # exclude this file in the analysis
#    foo2.fits   42 32   # mask OTA 42 and OTA 32
# if this file doesn't exist, the script will create an empty one
conf.ota_flag_file = conf.jobkey + '.ota'

# global naming convention for parsing and constructing intermediate filenames
# no need to change
input_fmt = 'ppa_{id[0]}_{name[0]}_odi_{band[0]}.fits'
conf.inglob = 'ppa_*odi_?.fits'
conf.inreg = (r'(?P<prefix>[^_]+_)?'
              r'(?P<imflag>[^_]+)_'
              r'(?P<id>20\d{6}T\d{6}\.\d)_(?P<name>.+)'
              r'_odi_(?P<band>\w)\.(?P<ext>.+)')

# bootstrap
conf.inputs = (
    os.path.join(input_root, input_glob),
    input_reg,
    os.path.join(conf.jobdir, input_fmt)
    )
pp_prep.tlist().chain(
    pp_astro.tlist).chain(
        pp_mosaic.tlist).chain(
            pp_photometry.tlist)
core.bootstrap()
