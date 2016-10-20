#! /bin/sh
#
# match_to_sdss.sh
# Copyright (C) 2016 Jerry Ma <jerry.ma.nk@gmail.com>
#
#----------------------------------------------------------------------------
#"THE BEER-WARE LICENSE" (Revision 42):
#Jerry wrote this file. As long as you retain this notice you
#can do whatever you want with this stuff. If we meet some day, and you think
#this stuff is worth it, you can buy me a beer in return Poul-Henning Kamp
#----------------------------------------------------------------------------


name=$1
sdss=$2
out=$3

icmd2='select "MAG_AUTO < 90. && MAGERR_AUTO >= 0.001 && FLAGS == 0"'

stilts tmatch2 matcher=sky in1=${sdss} ifmt1=ascii icmd1="${icmd1}" \
        in2=${name} ifmt2=ascii icmd2="${icmd2}" \
        values1="ra dec" values2="ALPHA_J2000 DELTA_J2000" \
        params=0.6 join=1and2 \
        out=${out} ofmt=ascii
