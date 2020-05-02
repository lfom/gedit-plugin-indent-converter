# -*- coding: utf-8 -*-
import gi
gi.require_version('Gedit', '3.0')
from gi.repository import GObject, Gio, Gdk, Gedit
import re
try:
    import gettext
    gettext.bindtextdomain('gedit-plugins')
    gettext.textdomain('gedit-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s

#Code based on https://github.com/theawless/Clear-Doc
class IndentConverterPluginAppActivatable(GObject.Object, Gedit.AppActivatable):
    app = GObject.property(type=Gedit.App)
    __gtype_name__ = "IndentConverterPluginAppActivatable"

    def __init__(self):
        GObject.Object.__init__(self)
        self.menu_ext = None
        self.menu_item = None

    def do_activate(self):
        self._build_menu()

    def _build_menu(self):
        # Get the extension from tools menu        
        self.menu_ext = self.extend_menu("tools-section")
        
        # This is the submenu which is added to a menu item and then inserted in tools menu.        
        sub_menu = Gio.Menu()
        sub_menu_item_spaces = Gio.MenuItem.new(_("_Spaces to tabs"), 'win.spaces_to_tabs')
        sub_menu.append_item(sub_menu_item_spaces)
        sub_menu_item_tabs = Gio.MenuItem.new(_("_Tabs to Spaces"), 'win.tabs_to_spaces')
        sub_menu.append_item(sub_menu_item_tabs)
        self.menu_item = Gio.MenuItem.new_submenu(_("_Indent Converter"), sub_menu)
        self.menu_ext.append_menu_item(self.menu_item)
        
        # Setting accelerators, first action is called when Ctrl+Alt+e is pressed. (PS: for some reason, using S and T do not work)
        self.app.set_accels_for_action("win.spaces_to_tabs", ("<Primary><Alt>E", None))
        self.app.set_accels_for_action("win.tabs_to_spaces", ("<Primary><Alt>A", None))

    def do_deactivate(self):
        self._remove_menu()

    def _remove_menu(self):
        # removing accelerators and destroying menu items
        self.app.set_accels_for_action("win.spaces_to_tabs", ())
        self.app.set_accels_for_action("win.tabs_to_spaces", ())
        self.menu_ext = None
        self.menu_item = None

class IndentConverterPluginWindowActivatable(GObject.Object, Gedit.WindowActivatable):

    __gtype_name__ = "IndentConverterPluginWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self._connect_menu()

    def do_deactivate(self):
        pass

    def do_update_state(self):
        view = self.window.get_active_view()

        #Enable if view exists and document is editable
        enabled = False
        enabled = view and view.get_editable()
        self.window.lookup_action('spaces_to_tabs').set_enabled(enabled)
        self.window.lookup_action('tabs_to_spaces').set_enabled(enabled)

    def _connect_menu(self):
        action_spaces = Gio.SimpleAction(name='spaces_to_tabs')
        action_spaces.connect('activate', self.do_spaces_to_tabs)
        self.window.add_action(action_spaces)
        action_tabs = Gio.SimpleAction(name='tabs_to_spaces')
        action_tabs.connect('activate', self.do_tabs_to_spaces)
        self.window.add_action(action_tabs)

    def remove_menu(self):
        pass

    def tab_size(self):
        settings = Gio.Settings.new('org.gnome.gedit.preferences.editor')
        tab_size = settings.get_uint('tabs-size')
        return tab_size
        
    def guess_tab_size(self, text):
        def gcd(a, b):
            return a if b == 0 else gcd(b, a % b);

        r = re.compile('^ +', re.MULTILINE)
        matches = r.findall(text)
        freq = {}

        # `key` - length of leading spaces, `value` - it's frequency
        for spaces in matches:
            spaces = len(spaces)
            if spaces in freq:
                freq[spaces] += 1
            else:
                freq[spaces] = 1

        # sort frequencies by value:
        items = [ [i[1], i[0]] for i in list(freq.items()) ]
        items.sort()
        items.reverse()
        items = [i[1] for i in items]

        if len(items) == 0:
            return 0
        elif len(items) == 1:
            return items[0]
        else:
            return gcd(items[0], items[1])

    def do_spaces_to_tabs(self, action, data):
    
        #TODO Code using view works?
        #view = self.window.get_active_view()
        #doc = view.get_buffer()
    
        #Return if document is empty
        doc = self.window.get_active_document()
        if doc is None:
            return
            
        #TODO Use selection if any, otherwise the whole document
        #try:
        #    start, end = doc.get_selection_bounds()
        #except ValueError:

        start, end = doc.get_bounds()
        text = doc.get_text(start, end, True)

        tab_size = self.guess_tab_size(text)
        if (tab_size < 2):
            tab_size = self.tab_size()
        r = re.compile('^(?:' +  (' ' * tab_size) + ')+', re.MULTILINE)

        def replacer(match):
            return '\t' * int(len(match.group(0)) / tab_size)

        text = r.sub(replacer, text)

        doc.begin_user_action()
        doc.set_text(text)
        doc.end_user_action()

    def do_tabs_to_spaces(self, action, data):
        doc = self.window.get_active_document()
        if doc is None:
            return
        
        start, end = doc.get_bounds()
        text = doc.get_text(start, end, True)
        text = text.expandtabs(self.tab_size())

        doc.begin_user_action()
        doc.set_text(text)
        doc.end_user_action()

