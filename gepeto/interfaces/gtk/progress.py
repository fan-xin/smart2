#
# Copyright (c) 2004 Conectiva, Inc.
#
# Written by Gustavo Niemeyer <niemeyer@conectiva.com>
#
# This file is part of Gepeto.
#
# Gepeto is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Gepeto is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gepeto; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
from gepeto.util.strtools import ShortURL, getSizeStr
from gepeto.progress import Progress, INTERVAL
import gobject, gtk
import posixpath
import thread
import time

class GtkProgress(Progress, gtk.Window):

    def __init__(self, hassub):
        Progress.__init__(self)
        gtk.Window.__init__(self)
        self.__gobject_init__()

        self._hassub = hassub
        self._fetchermode = False
        self._shorturl = ShortURL(50)
        self._ticking = False
        self._stopticking = False

        if hassub:
            self.set_size_request(500, 400)
        else:
            self.set_size_request(300, 80)

        self.set_title("Operation Progress")
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER)

        self._vbox = gtk.VBox()
        self._vbox.set_border_width(10)
        self._vbox.set_spacing(10)
        self._vbox.show()
        gtk.Window.add(self, self._vbox)

        self._topic = gtk.Label()
        self._topic.set_alignment(0, 0.5)
        self._topic.show()
        self._vbox.pack_start(self._topic, expand=False, fill=False)

        self._progress = gtk.ProgressBar()
        self._progress.set_size_request(-1, 25)
        self._progress.show()
        self._vbox.pack_start(self._progress, expand=False, fill=False)

        if hassub:
            self._scrollwin = gtk.ScrolledWindow()
            self._scrollwin.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
            self._scrollwin.set_shadow_type(gtk.SHADOW_IN)
            self._scrollwin.show()
            self._vbox.pack_start(self._scrollwin)

            self._treemodel = gtk.ListStore(gobject.TYPE_INT,
                                            gobject.TYPE_STRING,
                                            gobject.TYPE_STRING,
                                            gobject.TYPE_STRING)
            self._treeview = gtk.TreeView(self._treemodel)
            self._treeview.show()
            self._scrollwin.add(self._treeview)

            renderer = ProgressCellRenderer()
            column = gtk.TreeViewColumn("Progress", renderer, percent=0)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            column.set_fixed_width(110)
            self._treeview.append_column(column)

            renderer = gtk.CellRendererText()
            renderer.set_fixed_height_from_font(True)
            column = gtk.TreeViewColumn("Current", renderer, text=2)
            self._currentcolumn = column
            self._treeview.append_column(column)

            renderer = gtk.CellRendererText()
            renderer.set_fixed_height_from_font(True)
            column = gtk.TreeViewColumn("Total", renderer, text=3)
            self._totalcolumn = column
            self._treeview.append_column(column)

            renderer = gtk.CellRendererText()
            renderer.set_fixed_height_from_font(True)
            column = gtk.TreeViewColumn("Description", renderer, text=1)
            column.set_sizing(gtk.TREE_VIEW_COLUMN_FIXED)
            self._treeview.append_column(column)

            self._subiters = {}
            self._subindex = 0
            self._lastpath = None

    def setFetcherMode(self, flag):
        self._fetchermode = flag
        self._currentcolumn.set_visible(flag)
        self._totalcolumn.set_visible(flag)

    def tick(self):
        while not self._stopticking:
            self.lock()
            while gtk.events_pending():
                gtk.main_iteration()
            self.unlock()
            time.sleep(INTERVAL)
        self._ticking = False

    def start(self):
        Progress.start(self)

        self.setHasSub(self._hassub)
        self._ticking = True
        self._stopticking = False

        thread.start_new_thread(self.tick, ())

    def stop(self):
        self._stopticking = True
        while self._ticking: pass

        Progress.stop(self)

        if self._hassub:
            self._treemodel.clear()
            self._subiters.clear()
            self._subindex = 0
            self._lastpath = None

        self._shorturl.reset()

        gtk.Window.hide(self)

    def expose(self, topic, percent, subkey, subtopic, subpercent, data, done):
        gtk.Window.show(self)
        
        if self._hassub and subkey:
            if subkey in self._subiters:
                iter = self._subiters[subkey]
            else:
                iter = self._treemodel.append()
                self._subiters[subkey] = iter
                path = self._treemodel.get_path(iter)
                if self._lastpath:
                    column = self._treeview.get_column(1)
                    cellarea = self._treeview.get_cell_area(self._lastpath,
                                                            column)
                    cellarea.x, cellarea.y = self._treeview.\
                                             widget_to_tree_coords(cellarea.x,
                                                                   cellarea.y)
                    visiblearea = self._treeview.get_visible_rect()
                    isvisible = visiblearea.intersect(cellarea).height
                if not self._lastpath or isvisible:
                    self._treeview.scroll_to_cell(path, None, True, 0, 0)
                self._lastpath = path
            if self._fetchermode:
                subinfo = self.getSub(subkey)
                if subinfo and subinfo[1] > 1:
                    self._treemodel.set(iter, 2, getSizeStr(subinfo[0]),
                                              3, getSizeStr(subinfo[1]))
                subtopic = self._shorturl.get(subtopic)
            self._treemodel.set(iter, 0, subpercent, 1, subtopic)
        else:
            self._topic.set_text(topic)
            self._progress.set_fraction(percent/100.)
            self._progress.set_text("%d%%" % percent)
            if self._hassub:
                self._treeview.queue_draw()

gobject.type_register(GtkProgress)

class ProgressCellRenderer(gtk.GenericCellRenderer):

    __gproperties__ = {
        "percent": (gobject.TYPE_INT, "Percent", 
                    "Progress percentage", 0, 100, 0,
                    gobject.PARAM_READWRITE),
    }
                     
    def __init__(self):
        self.__gobject_init__()
        self.percent = 0

    def do_set_property(self, pspec, value):
        setattr(self, pspec.name, value)

    def do_get_property(self, pspec):
        return getattr(self, pspec.name)

    def on_render(self, window, widget, background_area,
                  cell_area, expose_area, flags):
        x_offset, y_offset, width, height = self.on_get_size(widget, cell_area)
        widget.style.paint_box(window, gtk.STATE_NORMAL, gtk.SHADOW_IN,
                               None, widget, "trough",
                               cell_area.x+x_offset, cell_area.y+y_offset,
                               width, height)
        xt = widget.style.xthickness
        xpad = self.get_property("xpad")
        space = (width-2*xt-2*xpad)*(self.percent/100.)
        widget.style.paint_box(window, gtk.STATE_PRELIGHT, gtk.SHADOW_OUT,
                               None, widget, "bar",
                               cell_area.x+x_offset+xt,
                               cell_area.y+y_offset+xt,
                               int(space), height-2*xt)

    def on_get_size(self, widget, cell_area):
        xpad = self.get_property("xpad")
        ypad = self.get_property("ypad")
        if cell_area:
            width = cell_area.width
            height = cell_area.height
            x_offset = xpad
            y_offset = ypad
        else:
            width = self.get_property("width")
            height = self.get_property("height")
            if width == -1: width = 100
            if height == -1: height = 30
            width += xpad*2
            height += ypad*2
            x_offset = 0
            y_offset = 0
        return x_offset, y_offset, width, height

gobject.type_register(ProgressCellRenderer)

def test():
    import sys, time

    prog = GtkProgress()

    data = {"item-number": 0}
    total, subtotal = 100, 100
    prog.start(True)
    prog.setTopic("Installing packages...")
    for n in range(1,total+1):
        data["item-number"] = n
        prog.set(n, total)
        prog.setSubTopic(n, "package-name%d" % n)
        for i in range(0,subtotal+1):
            prog.setSub(n, i, subtotal, subdata=data)
            prog.show()
            time.sleep(0.01)
    prog.stop()


if __name__ == "__main__":
    test()

# vim:ts=4:sw=4:et
