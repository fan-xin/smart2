#
# Copyright (c) 2004 Conectiva, Inc.
#
# Written by Gustavo Niemeyer <niemeyer@conectiva.com>
#
# This file is part of Smart Package Manager.
#
# Smart Package Manager is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# Smart Package Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Smart Package Manager; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from smart.option import OptionParser
from smart import *
import string
import re

USAGE="smart priority [options]"

DESCRIPTION="""
This command allows changing the priority of given packages.
Packages with higher priorities are considered a better option
even when package versions state otherwise. Using priorities
one may avoid unwanted upgrades, force downgrades, select
packages in given channels as preferential, and other kinds
of interesting setups. When a package has no explicit priority,
the channel priority is used. The channel priority may be
changed using the 'channel' command, and defaults to 0 when
not set.
"""

EXAMPLES="""
smart priority --set pkgname 100
smart priority --set pkgname mychannel -200
smart priority --remove pkgname 100
smart priority --remove pkgname mychannel -200
smart priority --show
smart priority --show pkgname
"""

def parse_options(argv):
    parser = OptionParser(usage=USAGE,
                          description=DESCRIPTION,
                          examples=EXAMPLES)
    parser.add_option("--set", action="store_true",
                      help="set priority")
    parser.add_option("--remove", action="store_true",
                      help="unset priority")
    parser.add_option("--show", action="store_true",
                      help="show priorities")
    parser.add_option("--force", action="store_true",
                      help="ignore problems")
    opts, args = parser.parse_args(argv)
    opts.args = args
    return opts

def main(ctrl, opts):

    priorities = sysconf.get("package-priorities", setdefault={})

    if opts.set:

        sysconf.assertWritable()

        if len(opts.args) == 2:
            name, priority = opts.args
            alias = None
        elif len(opts.args) == 3:
            name, alias, priority = opts.args
        else:
            raise Error, "Invalid arguments"

        try:
            priority = int(priority)
        except ValueError:
            raise Error, "Invalid priority"

        priorities.setdefault(name, {})[alias] = priority

    elif opts.remove:

        sysconf.assertWritable()

        if len(opts.args) == 1:
            name = opts.args[0]
            alias = None
        elif len(opts.args) == 2:
            name, alias = opts.args
        else:
            raise Error, "Invalid arguments"

        pkgpriorities = priorities.get(name)
        if pkgpriorities and alias in pkgpriorities:
            del pkgpriorities[alias]
            if not pkgpriorities:
                del priorities[name]
        elif not opts.force:
            raise Error, "Priority not found"

    elif opts.show:

        header = ("Package", "Channel", "Priority")
        print "%-30s %-20s %s" % header
        print "-"*(52+len(header[-1]))

        showpriorities = opts.args or priorities.keys()
        showpriorities.sort()

        for name in showpriorities:
            pkgpriorities = priorities.get(name)
            aliases = pkgpriorities.keys()
            aliases.sort()
            for alias in aliases:
                priority = pkgpriorities[alias]
                print "%-30s %-20s %d" % (name, alias or "*", priority)

        print

# vim:ts=4:sw=4:et
