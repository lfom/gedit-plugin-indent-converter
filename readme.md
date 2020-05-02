# Indent Converter plugin for Gedit

Converts tabs to spaces and spaces to tabs

[WIP]

~~Adds two items to **Edit** menu:~~

 - ~~**Convert spaces to tabs** - replaces all leading spaces with tabs in current document. It uses smart guess algorithm to guess the tab size used in the document. If that fails - uses tab size from gedit preferences.~~

 - ~~**Convert tabs to spaces** - replaces all leading tabs with spaces (size is taken from current gedit preferences) in current document.~~


## Installation

1. Download latest source package.
2. Copy `indent-converter.plugin` and `indent-converter.py` files to `~/.local/share/gedit/plugins/` (or `/usr/lib/gedit/plugins/` for system-wide installation).
3. Open (restart) Gedit.
4. Go to **Edit** - **Preferences** - **Plugins**.
5. Enable plugin.

### Translation

Please, contribute your languages.

### Fork text

***forked from [disfated/gedit-plugin-indent-converter](https://github.com/disfated/gedit-plugin-indent-converter)***

I just wanted to learn about Python and GTK integration, so I decided to update this plugin to newer Gedit using Python3.

*To Do*
- [x] Make it work in newer Gedit (tested on v3.34.0) using simple context menus
- [ ] Add shortcuts and menu entries to the Tools menu
- [ ] Add some commits from @bruno-schneider [repo](https://github.com/bruno-schneider/gedit-plugin-indent-converter) for easier install and i18n support

