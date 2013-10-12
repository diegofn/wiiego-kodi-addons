#/*
# *
# * ColombiaTV: ColombiaTV add-on for XBMC.
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
                
        # Main Menu Structure
        #     title,                    channelId,                  channelGroup,           image                    
        self.categories = (
            {'title':"Canal UNE",       'channelId':"205017",      'channelGroup':"8"      , 'image':"1026"},
            {'title':"UNE Manizales",   'channelId':"226978",      'channelGroup':"24"     , 'image':"1484"},
            {'title':"UNE Manizales",   'channelId':"215944",      'channelGroup':"23"     , 'image':"26616"},
            {'title':"TV5",             'channelId':"206412",      'channelGroup':"11"     , 'image':"26610"},
            {'title':"Canal U",         'channelId':"206416",      'channelGroup':"15"     , 'image':"1025"},
            {'title':"Telemedellin",    'channelId':"206414",      'channelGroup':"13"     , 'image':"1029"},
            {'title':"Teleantioquia",   'channelId':"205013",      'channelGroup':"4"      , 'image':"1007"},
            {'title':"TV Agro",         'channelId':"205015",      'channelGroup':"6"      , 'image':"1002"},
            {'title':"Cosmovision",     'channelId':"206415",      'channelGroup':"14"     , 'image':"809"},
            {'title':"Cable Noticias",  'channelId':"205016",      'channelGroup':"7"      , 'image':"1003"},
            {'title':"Televida",        'channelId':"205018",      'channelGroup':"9"      , 'image':"750"},
            {'title':"Trendy",          'channelId':"205019",      'channelGroup':"10"     , 'image':"26603"},
            {'title':"Humor",           'channelId':"206413",      'channelGroup':"12"     , 'image':"26604"},
            {'title':"Telecafe",        'channelId':"206417",      'channelGroup':"16"     , 'image':"1180"},
            {'title':"Nova",            'channelId':"206418",      'channelGroup':"17"     , 'image':"26606"},
            {'title':"Supermusica",     'channelId':"206419",      'channelGroup':"18"     , 'image':"26607"},
            {'title':"Click",           'channelId':"206577",      'channelGroup':"19"     , 'image':"26608"},
            {'title':"Life Design",     'channelId':"207384",      'channelGroup':"22"     , 'image':"26609"},
            {'title':"VMAS",            'channelId':"207642",      'channelGroup':"23"     , 'image':"26611"},
            {'title':"Mi Musica HD",    'channelId':"206731",      'channelGroup':"20"     , 'image':"26612"},
            {'title':"El Tiempo",       'channelId':"207648",      'channelGroup':"29"     , 'image':"26613"},
            {'title':"Yes",             'channelId':"205010",      'channelGroup':"1"     , 'image':"26614"},
            {'title':"UNEPREMIUM",      'channelId':"205017",      'channelGroup':"8"     , 'image':"9999"},
            {'title':"Televentas MIO",  'channelId':"205011",      'channelGroup':"2"     , 'image':"26615"}
            )

    def listMenu(self, params={}):
        self.common.log(repr(params), 1)
        get = params.get

        for category in self.categories:
            self.addListItem(params, category)
    
        self.xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        self.common.log("Done", 5)


    def addListItem(self, params={}, item_params={}):
        item = item_params.get

        # Add TV Channel
        contextmenu = [(self.language(3001), "XBMC.RunPlugin(%s?path=refresh)" % (sys.argv[0], ))]
        image = self.core.get_channel_image(item('image'))
        fanart = os.path.join(self.settings.getAddonInfo("path"), "fanart.jpg")

        listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
        listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
        listitem.setProperty("fanart_image", fanart)
        listitem.setInfo('Video', {'Title': item('title')})
        listitem.setProperty('IsPlayable', "true")
                
        url = self.core.get_channel_url(item('channelId'), item('channelGroup'))
        ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

        self.common.log("Done", 5)
