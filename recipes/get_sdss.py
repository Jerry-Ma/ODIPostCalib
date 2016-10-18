#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-09-17 21:46
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
get_sdss.py
"""

from astropy.table import Table
from astroquery.sdss import SDSS


if __name__ == '__main__':
    import sys

    sdss_filter, sky_layout, out_file = sys.argv[1:]
    entry = Table.read(sky_layout, format='ascii.commented_header')[-1]
    box = [entry['ramin'], entry['ramax'], entry['decmin'], entry['decmax']]

    # sdss_filter = re.match(r'.+odi_(\w).+', in_files[0]).group(1)
    # query sdss and get reference catalog
    sql_query = [
        "SELECT ra,dec,raErr,decErr,u,err_u,g,err_g,r,err_r,i,err_i,z,err_z",
        "FROM Star WHERE",
        "    ra BETWEEN {min_ra:f} and {max_ra:f}",
        "AND dec BETWEEN {min_dec:f} and {max_dec:f}",
        "AND ((flags_{filter:s} & 0x10000000) != 0)",     # detected in BINNED1
        # not EDGE, NOPROFILE, PEAKCENTER, NOTCHECKED, PSF_FLUX_INTERP,
        # SATURATED, or BAD_COUNTS_ERROR"
        "AND ((flags_{filter:s} & 0x8100000c00a4) = 0)",
        # not DEBLEND_NOPEAK or small PSF error
        "AND (((flags_{filter:s} & 0x400000000000) = 0) or "
        "(psfmagerr_{filter:s} <= 0.2))",
        # not INTERP_CENTER or not COSMIC_RAY
        "AND (((flags_{filter:s} & 0x100000000000) = 0) or "
        "(flags_{filter:s} & 0x1000) = 0)"]
    sql_query = '\n'.join(sql_query).format(
            filter=sdss_filter,
            min_ra=box[0], max_ra=box[1],
            min_dec=box[2], max_dec=box[3]
            )
    print sql_query
    stdstar = SDSS.query_sql(sql_query)
    stdstar.write(out_file, format='ascii.commented_header')
