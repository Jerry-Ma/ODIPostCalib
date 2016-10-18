#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-09-16 19:45
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
get_sky_layout.py

Get bounding box in ra and dec for a collection of images
"""


from extern.pyjerry.instrument.wiyn import WIYNFact

from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u
import numpy as np


def get_bbox(hdulist):
    coord = SkyCoord(hdulist[0].header['RA'], hdulist[0].header['DEC'],
                     unit=(u.hourangle, u.degree))
    ra = coord.ra.degree
    dec = coord.dec.degree
    (w, e), (s, n) = WIYNFact.get_bbox()
    bw = ra + w / np.cos(dec * np.pi / 180.)
    be = ra + e / np.cos(dec * np.pi / 180.)
    bs = dec + s
    bn = dec + n
    return bw, be, bs, bn


def get_min_max(l):
    minl = np.inf
    maxl = -np.inf
    dist = 0
    for i in l:
        for j in l:
            # TODO get handle of degree wrapping
            if np.abs(i - j) > dist:
                minl = min(i, j)
                maxl = max(i, j)
                dist = np.abs(i - j)
    if dist > 180.:
        print l
        raise RuntimeError(
            "there is degree wrapping that that code is not able to handle")
    return minl, maxl


def merge_bbox(box1, box2):
    if box1 is None:
        return box2
    elif box2 is None:
        return box1
    else:
        l1, r1, b1, t1 = box1
        l2, r2, b2, t2 = box2
        ramin, ramax = get_min_max([l1, l2, r1, r2])
        decmin, decmax = get_min_max([b1, b2, t1, t2])
        return ramin, ramax, decmin, decmax


def to_ds9_box(box):
    cra = (box[0] + box[1]) * 0.5
    cdec = (box[2] + box[3]) * 0.5
    dra = (box[1] - box[0]) * np.cos(cdec * np.pi / 180.)
    ddec = (box[3] - box[2])
    return cra, cdec, dra, ddec


if __name__ == "__main__":
    import os
    import sys
    from astropy.table import Table
    from astropy import wcs

    in_files = sys.argv[1:-3]
    out_file, out_reg, out_wcs = sys.argv[-3:]

    box = None
    tbl_out = []
    reg_out = []
    for image in in_files:
        print "working on image:", image
        hdulist = fits.open(image)
        ibox = get_bbox(hdulist)
        icra, icdec, iwidth, iheight = to_ds9_box(ibox)
        box = merge_bbox(box, ibox)
        tbl_out.append((
                os.path.basename(image),
                hdulist[0].header['OBJECT'],
                icra, icdec, iwidth, iheight,
                ibox[0], ibox[1], ibox[2], ibox[3],
                ))
        hdulist.close()
    cra, cdec, width, height = to_ds9_box(box)
    tbl_out.append((
        'all', 'all',
        cra, cdec, width, height,
        box[0], box[1], box[2], box[3]
        ))
    tbl_out = Table(np.array(tbl_out), names=[
        'filename', 'objname',
        'ra', 'dec', 'width', 'height',
        'ramin', 'ramax', 'decmin', 'decmax',
        ])
    tbl_out.write(out_file, format='ascii.commented_header')
    with open(out_reg, 'w') as fo:
        fo.write('global color=red\n')
        for entry in tbl_out[:-1]:
            filename, objname, icra, icdec, iwidth, iheight = [
                    entry[i] for i in range(6)]
            fo.write('fk5; box({0},{1},{2},{3}, 0) # text={{{4}}}\n'.format(
                    icra, icdec, iwidth, iheight, "{0} {1}".format(
                        os.path.splitext(filename)[0], objname)))
        fo.write('fk5; box({0},{1},{2},{3}, 0) # color=yellow'.format(
                cra, cdec, width, height))
    # create wcs file
    minra, maxra, mindec, maxdec = box
    if np.abs((maxra - minra) * (maxdec - mindec)) > 100.:
        raise RuntimeError(
                "catalog spans too wide range"
                " {0}--{1}, {2}--{3}".format(minra, maxra, mindec, maxdec))
    hdulist = fits.open(in_files[0])
    ow = wcs.WCS(hdulist[1].header)
    hdulist.close()
    ps = abs(ow.pixel_scale_matrix[0, 0])
    ncol = width / ps
    nrow = height / ps
    ow.wcs.crpix = [ncol / 2, nrow / 2]
    # ow.wcs.cdelt = np.diag(ow.pixel_scale_matrix)
    ow.wcs.crval = [cra, cdec]
    ow.wcs.ctype = ["RA---STG", "DEC--STG"]
    header = ow.to_header()
    # for key in ['PC1_1', 'PC1_2', 'PC2_1', 'PC2_2']:
    #     header[key.replace('PC', 'CD')] = header[key]
    header['CD1_1'] = ps
    header['CD2_2'] = -ps
    header['CD1_2'] = 0
    header['CD2_1'] = 0
    keepkeys = ['EQUINOX', 'RADESYS',
                'CTYPE1', 'CUNIT1', 'CRVAL1', 'CRPIX1', 'CD1_1', 'CD1_2',
                'CTYPE2', 'CUNIT2', 'CRVAL2', 'CRPIX2', 'CD2_1', 'CD2_2',
                ]
    for key in header.keys():
        if key not in keepkeys:
            del header[key]
    header.insert(0, ('EXTEND', True))
    header.insert(0, ('NAXIS2', int(nrow + 0.5)))
    header.insert(0, ('NAXIS1', int(ncol + 0.5)))
    header.insert(0, ('NAXIS', 2))
    header.insert(0, ('BITPIX', 0))
    header.insert(0, ('SIMPLE', True))
    # print header
    with open(out_wcs, 'w') as fo:
        fo.write(header.tostring())
