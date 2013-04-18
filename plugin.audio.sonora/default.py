#/*
# *
# * Sonora: Sonora add-on for XBMC.
# *
# * Copyright (C) 2013 Wiiego
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
version = "1.0.1"
plugin   = 'Sonora-' + version
author = 'Wiiego'

# XBMC Hooks
settings = xbmcaddon.Addon(id='plugin.audio.sonora')
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
    import SonoraPluginSettings
    pluginsettings = SonoraPluginSettings.SonoraPluginSettings()
    import SonoraCore
    core = SonoraCore.SonoraCore()
    import SonoraLogin
    login = SonoraLogin.SonoraLogin()
    import SonoraNavigation
    navigation = SonoraNavigation.SonoraNavigation()

    if (not sys.argv[2]):
        common.log("Login")
        login.login()
        navigation.listMenu()

    else:
		login.login()
		params = common.getParameters(sys.argv[2])
		get = params.get
		
		if (get("action")):
			navigation.executeAction(params)
		elif (get("path")):
			navigation.listMenu(params)
		else:
			common.log("ARGV Nothing done.. verify params " + repr(params), 5)

