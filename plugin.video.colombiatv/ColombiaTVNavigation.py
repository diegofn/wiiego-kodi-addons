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
                

    def listMenu(self):
        # Parse channels from json
        elements = self.core.getChannelList()

        for element in elements:
            self.addListItem(element)
    
        self.xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        print ("Done")
    

    def playStream(self, mode, params={}):
        # Find the URL to play
        stream_url = None
        stream_listitem = None

        if mode == 'brightcove':  
            stream_url = self.core.getBrightcove( params('channelid'), params('url') )
        elif mode == 'fog':  
            stream_url = self.core.getFog( params ('url'), params('channelid') )
        elif mode == 'p2pcast':  
            stream_url = self.core.getP2pcast( params('channelid') )
        elif mode == 'caston':  
            stream_url = self.core.getCastOn( params('channelid') )
        elif mode == 'lw':  
            stream_url = self.core.getLw( params('channelid'), params('pass') )
        elif mode == 'publisher':  
            stream_url = self.core.getPublisher( params('host'), params('channelid') )
        elif mode == 'pxstream':  
            stream_url = self.core.getPxstream( params('url'), params('channelid') )
        elif mode == 'nowlive':  
            stream_url = self.core.getNowLive( params('url'), params('channelid') )
        elif mode == 'widestream':  
            stream_url = self.core.getWideStream( params('url'), params('channelid') )
        elif mode == 'hqq':  
            stream_url = self.core.getHqq( params('vid') )
        elif mode == 'eb':  
            stream_url = self.core.getEb( params('channelid'), params('url') )
        elif mode == 'random':  
            stream_url = self.core.getRandom( params('host'), params('url'), params('referer') )
        elif mode == 'bro.adca.st':  
            stream_url = self.core.getBroadcastSite( params('channelid'), params('url') )
        elif mode == 'rcnapp':  
            stream_url = self.core.getRCNApp( )
        elif mode == 'cvhls':  
            stream_listitem = self.core.getCVHLS( params('url') )
        elif mode == 'radiotime':  
            stream_url = self.core.getRadiotime( params('station') )
        elif mode == 'gamovideo':  
            stream_url = self.core.getGamovideo( params('vid') )
        elif mode == 'streamango':  
            stream_url = self.core.getStreamango( params('vid') )
        elif mode == 'kastream':  
            stream_url = self.core.getKastream( params('url'), params('channelid') )
        elif mode == 'whostreams':  
            stream_url = self.core.getWhostreams( params('url'), params('channelid') )
        elif mode == 'telerium':  
            stream_url = self.core.getTeleriumTV( params('channelid'), params('url') )
        elif mode == 'cvmpd':  
            stream_listitem = self.core.getCVMPD( params('url'), params('url_webapi') )
                
        if (stream_listitem == None):
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=stream_url))  
        else:
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, stream_listitem)  


    def addListItem(self, item_params={}):
        item = item_params.get

        # Add TV Channel
        contextmenu = [(self.language(3001), "XBMC.RunPlugin(%s?path=refresh)" % (sys.argv[0], ))]
        image = item('image')
        fanart = os.path.join(self.settings.getAddonInfo("path"), "fanart.jpg")

        #
        # Dont add the 0 channeld (update item) if the user has the latest version
        # ColombiaPlay and ColombiaRadio is the 100 id 
        #
        if item('id') == '0':
            print ("Check for new version")
            if re.search(self.common.version, item('title')):
                print ("You have the latest version: " + self.common.version)
            else:
                listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
                listitem.setProperty("fanart_image", fanart)
                listitem.setInfo('Video', {'Title': item('title')})
                listitem.setProperty('IsPlayable', "false")
                ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=False)

        elif item('id') == '100':
            print ("ColombiaRadio and ColombiaTV Main Menu")
            listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
            listitem.setProperty("fanart_image", fanart)
            ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=True)

        else:
            listitem = self.xbmcgui.ListItem(label=item('title'), label2='TV Show', iconImage=image, thumbnailImage=image)
            listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
            listitem.setProperty("fanart_image", fanart)
            #listitem.setInfo('Video', {'Title': item('title'), 'MediaType': 'tvshow', 'Plot': '[B]' + item('title') + '[/B] Plot'})
            listitem.setInfo('video',
                {   'title': item('title'),
                    'mediatype': 'tvshow',
                    'plot': '[B]' + item('title') + '[/B][CR][CR]Plot[CR]TV Show description',
                    'tagline': 'Tag yo',
                    'genre': ['Infantil'],
                    'tag': ['Series','Infantil','Children']
                })
            listitem.setProperty('IsPlayable', "true")
            ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=False) 
    