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

import sys
import urllib
import os
import re

class ColombiaTVNavigation():
    def __init__(self):
        self.xbmc = sys.modules["__main__"].xbmc
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        self.xbmcplugin = sys.modules["__main__"].xbmcplugin

        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        self.language = sys.modules["__main__"].language
        self.core = sys.modules["__main__"].core
        self.common = sys.modules["__main__"].common

        self.pluginsettings = sys.modules["__main__"].pluginsettings
                

    def listMenu(self, params={}):
        self.common.log(repr(params), 1)
        get = params.get

        # Parse channels from json
        elements = self.core.get_channel_list()

        for element in elements:
            self.addListItem(params, element)
    
        self.xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        self.common.log("Done", 5)


    def addListItem(self, params={}, item_params={}):
        item = item_params.get

        # Add TV Channel
        contextmenu = [(self.language(3001), "XBMC.RunPlugin(%s?path=refresh)" % (sys.argv[0], ))]
        image = item('image')
        fanart = os.path.join(self.settings.getAddonInfo("path"), "fanart.jpg")

        listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
        listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
        listitem.setProperty("fanart_image", fanart)
        listitem.setInfo('Video', {'Title': item('title')})
        listitem.setProperty('IsPlayable', "true")
                
        ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=False)

        self.common.log("Done", 5)
