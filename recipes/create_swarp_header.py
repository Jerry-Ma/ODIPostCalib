#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-08-20 02:04
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
create_swarp_header.py
"""


def get_flux_scale(hdr):
    ret = []
    with open(hdr, 'r') as fo:
        for ln in fo.readlines():
            ln = ln.strip()
            if ln.startswith('FLXSCALE'):
                scale = float(ln.split('=')[1].split('/')[0])
                ret.append(scale)
    return ret


if __name__ == "__main__":
    import sys
    sc_header, wcs_header, out_header = sys.argv[1:]
    out_lines = []
    scales = get_flux_scale(sc_header)
    i = 0
    with open(wcs_header, 'r') as fo:
        has_pv1_3 = False
        has_pv2_3 = False
        for oln in fo.readlines():
            ln = oln.strip()
            if ln.startswith('FLXSCALE'):
                ln = "{0:8s}={1:>21s}{2:s}\n".format(
                    "FLXSCALE", str(scales[i]), " / sc flux scale to zp=25")
                i += 1
            else:
                ln = oln
            if ln.startswith('PV1_3'):
                has_pv1_3 = True
            elif ln.startswith('PV2_3'):
                has_pv2_3 = True
            elif ln.strip() == 'END':
                if not has_pv1_3:
                    out_lines.append(
                        "{0:8s}={1:>21s}{2:s}\n".format(
                            "PV1_3", str(0.0), " / fix scamp missing key"))
                if not has_pv2_3:
                    out_lines.append(
                        "{0:8s}={1:>21s}{2:s}\n".format(
                            "PV2_3", str(0.0), " / fix scamp missing key"))
                has_pv1_3 = False
                has_pv2_3 = False
            out_lines.append(ln)
    with open(out_header, 'w') as fo:
        for ln in out_lines:
            fo.write(ln)
