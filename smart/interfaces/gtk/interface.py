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
from smart.interfaces.gtk.progress import GtkProgress
from smart.interfaces.gtk.changes import GtkChanges
from smart.interfaces.gtk.log import GtkLog
from smart.interface import Interface
from smart.fetcher import Fetcher
from smart.const import DEBUG
from smart import *
from gi.repository import Gtk
import sys

class GtkInterface(Interface):

    def __init__(self, ctrl):
        Interface.__init__(self, ctrl)
        self._log = GtkLog()
        self._progress = GtkProgress(False)
        self._hassubprogress = GtkProgress(True)
        self._changes = GtkChanges()
        self._window = None
        self._sys_excepthook = sys.excepthook

    def run(self, command=None, argv=None):
        self.setCatchExceptions(True)
        result = Interface.run(self, command, argv)
        self.setCatchExceptions(False)
        return result

    def eventsPending(self):
        return Gtk.events_pending()

    def processEvents(self):
        Gtk.main_iteration()

    def getProgress(self, obj, hassub=False):
        if hassub:
            self._progress.hide()
            fetcher = isinstance(obj, Fetcher) and obj or None
            self._hassubprogress.setFetcher(fetcher)
            return self._hassubprogress
        else:
            self._hassubprogress.hide()
            return self._progress

    def getSubProgress(self, obj):
        return self._hassubprogress

    def askYesNo(self, question, default=False):
        dialog = Gtk.MessageDialog(parent=self._window,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.QUESTION,
                                   buttons=Gtk.ButtonsType.YES_NO,
                                   message_format=question)
        dialog.set_transient_for(self._window)
        dialog.set_default_response(default and Gtk.ResponseType.YES
                                             or Gtk.ResponseType.NO)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.YES:
            return True
        elif response == Gtk.ResponseType.NO:
            return False
        else:
            return default

    def askContCancel(self, question, default=False):
        if question[-1] not in ".!?":
            question += "."
        return self.askYesNo(question+_(" Continue?"), default)

    def askOkCancel(self, question, default=False):
        dialog = Gtk.MessageDialog(parent=self._window,
                                   flags=Gtk.DialogFlags.MODAL,
                                   type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK_CANCEL,
                                   message_format=question)
        dialog.set_transient_for(self._window)
        dialog.set_default_response(default and Gtk.ResponseType.OK
                                             or Gtk.ResponseType.CANCEL)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK:
            return True
        elif response == Gtk.ResponseType.CANCEL:
            return False
        else:
            return default

    def askInput(self, prompt, message=None, widthchars=40, echo=True):
        dialog = Gtk.Dialog(_("Input"),
                            parent=self._window,
                            flags=Gtk.DialogFlags.MODAL,
                            buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK,
                                     Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL),
                            )
        dialog.set_transient_for(self._window)
        vbox = Gtk.VBox()
        vbox.set_border_width(10)
        vbox.set_spacing(10)
        vbox.show()
        dialog.vbox.pack_start(vbox, False, False)
        if message:
            label = Gtk.Label(label=message)
            label.set_alignment(0.0, 0.5)
            label.show()
            vbox.pack_start(label, False, True)
        hbox = Gtk.HBox()
        hbox.set_spacing(10)
        hbox.show()
        vbox.pack_start(hbox, True, True, 0)
        label = Gtk.Label(label=prompt)
        label.show()
        hbox.pack_start(label, False, False)
        entry = Gtk.Entry()
        entry.set_width_chars(widthchars)
        if not echo:
            entry.set_visibility(False)
            entry.set_invisible_char('*')
        entry.show()
        hbox.pack_start(entry, True, True, 0)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            result = entry.get_text()
        else:
            result = ""
        dialog.destroy()
        return result

    def insertRemovableChannels(self, channels):
        question = _("Insert one or more of the following removable "
                     "channels:\n")
        question += "\n"
        for channel in channels:
            question += "    "
            question += channel.getName()
            question += "\n"
        return self.askOkCancel(question, default=True)

    def message(self, level, msg):
        self._log.message(level, msg)

    def confirmChange(self, oldchangeset, newchangeset, expected=1):
        changeset = newchangeset.difference(oldchangeset)
        keep = []
        for pkg in oldchangeset:
            if pkg not in newchangeset:
                keep.append(pkg)
        if len(keep)+len(changeset) <= expected:
            return True
        return self._changes.showChangeSet(changeset, keep=keep, confirm=True)

    def confirmChangeSet(self, changeset):
        return self._changes.showChangeSet(changeset, confirm=True)

    # Non-standard interface methods

    def _excepthook(self, type, value, tb):
        if issubclass(type, Error) and not sysconf.get("log-level") is DEBUG:
            self._hassubprogress.hide()
            self._progress.hide()
            iface.error(str(value[0]))
        else:
            import traceback
            lines = traceback.format_exception(type, value, tb)
            iface.error("\n".join(lines))

    def setCatchExceptions(self, flag):
        if flag:
            sys.excepthook = self._excepthook
        else:
            sys.excepthook = self._sys_excepthook

    def hideProgress(self):
        self._progress.hide()
        self._hassubprogress.hide()

