#!/usr/bin/python
from epm.option import OptionParser
from epm import *
import sys

VERSION = "0.0.1"

HELP = """\
Usage: epm command [options] [arguments]

Available commands:
    query

Run "epm command --help" for more information.

Written by Gustavo Niemeyer <niemeyer@conectiva.com>.
"""

def parse_options(argv):
    parser = OptionParser(help=HELP, version=VERSION)
    parser.disable_interspersed_args()
    parser.add_option("-c", dest="conffile", metavar="FILE",
                      help="configuration file (default is "
                           "~/.epm/config or /etc/epm.conf)")
    parser.add_option("--log", dest="loglevel", metavar="LEVEL",
                      help="set logging level to LEVEL (debug, info, "
                           "warning, error)", default="warning")
    opts, args = parser.parse_args()
    if len(args) < 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    opts.command = args[0]
    opts.argv = args[1:]
    return opts

def main(argv):
    opts = parse_options(argv)
    try:
        try:
            epm_module = __import__("epm.commands."+opts.command)
            commands_module = getattr(epm_module, "commands")
            command_module = getattr(commands_module, opts.command)
        except (ImportError, AttributeError):
            if opts.loglevel == "debug":
                import traceback
                traceback.print_exc()
                sys.exit(1)
            raise Error, "invalid command '%s'" % command
        cmdopts = command_module.parse_options(opts.argv)
        opts.__dict__.update(cmdopts.__dict__)
        command_module.main(opts)
    except Error, e:
        sys.stderr.write("error: %s\n" % str(e))
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv[1:])

# vim:ts=4:sw=4:et
