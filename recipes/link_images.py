#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Create Date    :  2016-09-18 10:18
# Python Version :  2.7.12
# Git Repo       :  https://github.com/Jerry-Ma
# Email Address  :  jerry.ma.nk@gmail.com
"""
link_images.py
"""

from common import get_image_flag
import os


def create_or_check_link(in_file, out_file):
    if os.path.exists(out_file):
        if os.path.samefile(in_file, out_file):
            print "link exists, skip"
            return None
        elif os.path.islink(out_file):
            print "link exists but mismatch, unlink"
            os.unlink(out_file)
        else:
            raise RuntimeError("file link not consistent {0}".format(
                in_file, out_file))
    print "link {0}".format(in_file)
    os.symlink(
            os.path.relpath(in_file, os.path.dirname(out_file)),
            out_file)


def remove_link_if_exist(out_file):
    if not os.path.exists(out_file):
        print "there is no link, skip"
        return
    elif os.path.islink(out_file):
        print "remove link for {0}".format(in_file)
        os.unlink(out_file)
    else:
        raise RuntimeError("not a link {0}".format(out_file))


if __name__ == "__main__":
    import sys
    index_file, in_file, flag_file, out_file = sys.argv[1:]
    flag = get_image_flag(index_file, flag_file)
    print "flag: {0}".format(flag)
    if -1 in flag:
        remove_link_if_exist(out_file)
    else:
        create_or_check_link(in_file, out_file)
