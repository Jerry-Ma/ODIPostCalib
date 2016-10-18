#! /bin/sh
#
# setup_astromatic.sh
# Copyright (C) 2016 Jerry Ma <jerry.ma.nk@gmail.com>
#
#----------------------------------------------------------------------------
#"THE BEER-WARE LICENSE" (Revision 42):
#Jerry wrote this file. As long as you retain this notice you
#can do whatever you want with this stuff. If we meet some day, and you think
#this stuff is worth it, you can buy me a beer in return Poul-Henning Kamp
#----------------------------------------------------------------------------


ambin="astromatic/bin"
amshare="astromatic/share"
mkdir -p $ambin
mkdir -p $amshare
for prog in 'sextractor' 'scamp' 'swarp' 'ldactoasc'; do
    if [[ $prog == 'sextractor' ]]; then
        binprog='sex'
    else
        binprog=$prog
    fi
    bin=$(which $binprog)
    if [[ -x $bin ]]; then
        bindir=$(dirname $bin)
        echo "found $prog in $bindir"
        echo ln -sf $(readlink -m $bin) $ambin
        ln -sf $(readlink -m $bin) $ambin
        sharedir=$bindir/../share/${prog}
        if [[ -d $sharedir ]]; then
            echo "found share directory for $prog $sharedir"
            echo ln -sf $(readlink -m $sharedir) $amshare
            ln -sf $(readlink -m $sharedir) $amshare
        fi
    else
        echo "not able to find $prog"
    fi
done
