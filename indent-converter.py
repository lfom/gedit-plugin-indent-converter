# -*- coding: utf-8 -*-
from gi.repository import GObject, Gedit, Gtk, Gio
import re
try:
    import gettext
    gettext.bindtextdomain('gedit-plugins')
    gettext.textdomain('gedit-plugins')
    _ = gettext.gettext
except:
    _ = lambda s: s


UI_XML = """<ui>
    <menubar name='MenuBar'>
        <menu name='EditMenu' action='Edit'>
            <placeholder name='EditOps_6'>
                <menu action='TabConvert'>
                    <menuitem action='SpacesToTabs'/>
                    <menuitem action='TabsToSpaces'/>
                </menu>
            </placeholder>
        </menu>
    </menubar>
</ui>"""


class IndentConverterPluginWindowActivatable(GObject.Object, Gedit.WindowActivatable):

    __gtype_name__ = "IndentConverterPluginWindowActivatable"

    window = GObject.property(type=Gedit.Window)

    def __init__(self):
        GObject.Object.__init__(self)

    def do_activate(self):
        self.insert_menu()
        
        #Add contextual menu entries
        action = Gio.SimpleAction(name="spacestotabs")
        action.connect('activate', lambda a, p: self.do_spaces_to_tabs())
        self.window.add_action(action)

        action = Gio.SimpleAction(name="tabstospaces")
        action.connect('activate', lambda a, p: self.do_tabs_to_spaces())
        self.window.add_action(action)

    def do_deactivate(self):
        self.remove_menu()
        
        #Remove contextual menu entries
        self.window.remove_action("spacestotabs")
        self.window.remove_action("tabstospaces")

    def do_update_state(self):
        view = self.window.get_active_view()

        #Enable if view exists and document is editable
        enabled = False
        enabled = view and view.get_editable()
        self.window.lookup_action('spacestotabs').set_enabled(enabled)
        self.window.lookup_action('tabstospaces').set_enabled(enabled)
        
        #self.action_group.set_sensitive(bool(view and view.get_editable()))

    def insert_menu(self):
        pass
#        manager = self.window.get_ui_manager()
#        self.action_group = Gtk.ActionGroup('IndentConverterActions')
#        self.action_group.add_actions([
#            ('TabConvert', None, _('Convert Tabs'), None, None, None),
#            ('SpacesToTabs', Gtk.STOCK_INDENT, _('Convert spaces to tabs'),
#                None, _('Convert spaces to tabs'), self.do_spaces_to_tabs),
#            ('TabsToSpaces', Gtk.STOCK_INDENT, _('Convert tabs to spaces'),
#                None, _('Convert tabs to spaces'), self.do_tabs_to_spaces),
#        ])
#        manager.insert_action_group(self.action_group, -1)
#        self.ui_id = manager.add_ui_from_string(UI_XML)

    def remove_menu(self):
        pass
#        manager = self.window.get_ui_manager()
#        manager.remove_ui(self.ui_id)
#        manager.remove_action_group(self.action_group)
#        manager.ensure_update()

    def do_spaces_to_tabs(self):
        view = self.window.get_active_view()
        if view and hasattr(view, "indent_converter_plugin_view_activatable"):
            view.indent_converter_plugin_view_activatable.do_spaces_to_tabs()
    
    def do_tabs_to_spaces(self):
        view = self.window.get_active_view()
        if view and hasattr(view, "indent_converter_plugin_view_activatable"):
            view.indent_converter_plugin_view_activatable.do_tabs_to_spaces()
            
class IndentConverterPluginViewActivatable(GObject.Object, Gedit.ViewActivatable):   

    __gtype_name__ = "IndentConverterPluginViewActivatable"

    view = GObject.Property(type=Gedit.View)

    def __init__(self):
        self.popup_handler_id = 0
        GObject.Object.__init__(self)

    def do_activate(self):
        self.view.indent_converter_plugin_view_activatable = self
        self.popup_handler_id = self.view.connect('populate-popup', self.populate_popup)

    def do_deactivate(self):
        if self.popup_handler_id != 0:
            self.view.disconnect(self.popup_handler_id)
            self.popup_handler_id = 0
        delattr(self.view, "indent_converter_plugin_view_activatable")

    def populate_popup(self, view, popup):
        if not isinstance(popup, Gtk.MenuShell):
            return

        item = Gtk.SeparatorMenuItem()
        item.show()
        popup.append(item)

        item = Gtk.MenuItem.new_with_mnemonic(_("_Spaces to Tabs"))
        item.set_sensitive(self.view.get_editable())
        item.show()
        item.connect('activate', lambda i: self.do_spaces_to_tabs())
        popup.append(item)

        item = Gtk.MenuItem.new_with_mnemonic(_('_Tabs to Spaces'))
        item.set_sensitive(self.view.get_editable())
        item.show()
        item.connect('activate', lambda i: self.do_tabs_to_spaces())
        popup.append(item)

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

    def do_spaces_to_tabs(self):
        #Return if document is empty
        doc = self.view.get_buffer()
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

    def do_tabs_to_spaces(self):
        doc = self.view.get_buffer()
        if doc is None:
            return
        
        start, end = doc.get_bounds()
        text = doc.get_text(start, end, True)
        text = text.expandtabs(self.tab_size())

        doc.begin_user_action()
        doc.set_text(text)
        doc.end_user_action()

