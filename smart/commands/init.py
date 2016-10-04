#
# Copyright (C) 2016 FUJITSU LIMITED
#
# Written by Fan Xin <fan.xin@jp.fujitsu.com>
# 2016-08-28
# 
# This file is part of Smart2 Package Manager
#
# This file provides the init command
# Usage: smart init
# 

from smart.transaction import Transaction, PolicyInstall, sortUpgrades
from smart.transaction import INSTALL, REINSTALL
from smart.option import OptionParser
from smart.cache import Package
from smart import *
import string
import re
import os
import pdb
import sys

#use debug module
#pdb.set_trace()

USAGE=_("smart init [pacakge repository path] [rootfs path] ")

DESCRIPTION=_("""
This command will initial the environment before using smart2.
""")

EXAMPLES=_("""
smart install pkgname
smart install '*kgna*'
smart install pkgname-1.0
smart install pkgname-1.0-1
smart install pkgname1 pkgname2
smart install ./somepackage.file
smart install http://some.url/some/path/somepackage.file
""")

def add (num1=0, num2=0):
    return int(num1) + int(num2)

def sub(num1=0, num2=0):
    return int(num1) - int(num2)
#def main(ctrl, opts):

def option_parser():
    parser = OptionParser(usage=USAGE,
                          description=DESCRIPTION,
                          examples=EXAMPLES)
    parser.add_option("--info", action="store_true",
                      help=_("Fan Xin"))
    parser.add_option("--paths", action="store_true",
                      help=_("show path list"))
    parser.add_option("--changelog", action="store_true",
                      help=_("show change log"))
    return parser


def parse_options(argv):
    parser = option_parser()
    opts, args = parser.parse_args(argv)
    opts.args = args
    return opts

def main(ctrl, opts):
    
    print sys.argv
    #pdb.set_trace() #break point added here
    addition = add(sys.argv[1], sys.argv[2])
    print addition
    subtraction = sub(sys.argv[1], sys.argv[2])
    print subtraction
    
    print "Hello, this is smart init command."

#if __name__ == '__main__':
#    main()

# vim:ts=4:sw=4:et
