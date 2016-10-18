#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-09-17 21:33
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
get_gsc.py
"""

import numpy as np
from astropy.table import Table
from astropy.table import Column
import requests


if __name__ == '__main__':
    import sys

    param, sky_layout, out_file = sys.argv[1:]
    bright_star_mag = float(param)
    synth_mag_lim = bright_star_mag + 2
    entry = Table.read(sky_layout, format='ascii.commented_header')[-1]
    box = [entry['ramin'], entry['ramax'], entry['decmin'], entry['decmax']]
    # query guide star catalog
    url = 'http://gsss.stsci.edu/webservices/vo/CatalogSearch.aspx'
    payload = {
            'BBOX': '{0},{1},{2},{3}'.format(box[0], box[2], box[1], box[3]),
            'FORMAT': 'VOTable', 'CAT': 'GSC23'}
    # print payload
    response = requests.get(url=url, params=payload)
    if response.status_code == requests.codes.ok:
        outcol = ['ra', 'dec', 'FpgMag', 'JpgMag', 'NpgMag']
        with open(out_file, 'w') as fo:
            fo.write(response.text)
        # filter the catalog
        cat = Table.read(out_file, format='votable')
        cat = cat[(cat['FpgMag'] < synth_mag_lim) |
                  (cat['JpgMag'] < synth_mag_lim) |
                  (cat['NpgMag'] < synth_mag_lim)
                  ][outcol]
        # create synthesis mag column based on mean color
        mcol = 'FpgMag'
        mag = cat[mcol]
        for col in ['JpgMag', 'NpgMag']:
            gmask = (mag < 90) & (cat[col] < 90)
            offset = np.mean(mag[gmask] - cat[col][gmask])
            bmask = (mag > 90) & (cat[col] < 90)
            mag[bmask] = cat[col][bmask] + offset
        cat.add_column(Column(mag, name='mag'))
        cat = cat[cat['mag'] < bright_star_mag]
        cat.write(out_file, format='ascii.commented_header')
