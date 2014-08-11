#/*
# *
# * ColombiaTV: ColombiaTV add-on for XBMC.
# *
# * Copyright (C) 2013-2014 Wiiego
# *
# * This program is free software: you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation, either version 3 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *	
# * You should have received a copy of the GNU General Public License
# * along with this program.  If not, see <http://www.gnu.org/licenses/>.
# *
# */

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib
import re

# Set global values.
version = "1.0.5"
plugin   = 'ColombiaTV-' + version
author = 'Wiiego'

# XBMC Hooks
settings = xbmcaddon.Addon(id='plugin.video.colombiatv')
language = settings.getLocalizedString
enabledebug = settings.getSetting('enabledebug') == "true"

# WISH. Initialise caches.

# Enable HTTP Cookies.
cookie = cookielib.LWPCookieJar()
cookie_handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(cookie_handler)

# Plugin Main
if (__name__ == "__main__" ):
    if enabledebug:
        print("ARGV Parameters: " + repr(sys.argv))
   
    import CommonFunctions as common
    common.plugin = plugin
    import ColombiaTVPluginSettings
    pluginsettings = ColombiaTVPluginSettings.ColombiaTVPluginSettings()
    import ColombiaTVCore
    core = ColombiaTVCore.ColombiaTVCore()
    import ColombiaTVNavigation
    navigation = ColombiaTVNavigation.ColombiaTVNavigation()

    navigation.listMenu()

