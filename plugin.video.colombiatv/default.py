#/*
# *
# * ColombiaTV: ColombiaTV add-on for Kodi.
# *
# * Copyleft 2013-2018 Wiiego
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
# *  based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# */

import xbmc, xbmcgui, xbmcplugin, xbmcaddon
import os, urllib, urllib2, cookielib
import ssl
import re

# Set global values.
version = "1.5.5"
plugin   = 'ColombiaTV-' + version
author = 'Wiiego'

# XBMC Hooks
settings = xbmcaddon.Addon(id='plugin.video.colombiatv')
language = settings.getLocalizedString
enabledebug = settings.getSetting('enabledebug') == "true"

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
    common.version = version
    import ColombiaTVPluginSettings
    pluginsettings = ColombiaTVPluginSettings.ColombiaTVPluginSettings()
    import ColombiaTVCore
    core = ColombiaTVCore.ColombiaTVCore()
    import MiTVIntegration
    mitvEpg = MiTVIntegration.MiTVIntegration()
    import ColombiaTVNavigation
    navigation = ColombiaTVNavigation.ColombiaTVNavigation()
    import ColombiaPlayNavigation
    navigationPlay = ColombiaPlayNavigation.ColombiaPlayNavigation()
    import ColombiaRadioNavigation
    navigationRadio = ColombiaRadioNavigation.ColombiaRadioNavigation()
    
    # Parse the parameters
    paramters = {}
    try:
        paramters = dict( arg.split( "=" ) for arg in ((sys.argv[2][1:]).split( "&" )) )
        for key in paramters:
           paramters[key] = core.demunge(paramters[key])
    except:
        paramters = {}

    p = paramters.get
    mode = p('mode', None)
    
    #
    # Addon service:
    # * List available streams
    # * List on demand shows
    # * Play channel streams 
    #
    if mode ==  None:
        navigation.listMenu()
      
    elif mode == 'colombiaplay': 
        navigationPlay.listMenu( p('show') )
    elif mode == 'colombiaradio': 
        navigationRadio.listMenu( p('station') )
    else:
        navigation.playStream( mode, p )
    


