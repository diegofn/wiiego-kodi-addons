#/*
# *
# * ColombiaTV: ColombiaTV add-on for Kodi.
# *
# * Copyleft 2013-2020 Wiiego
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
import os
import re

class ColombiaTVNavigation():
    def __init__(self):
        self.xbmc = sys.modules["__main__"].xbmc
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        self.xbmcplugin = sys.modules["__main__"].xbmcplugin

        self.addon = sys.modules["__main__"].addon
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        self.enabledeveloper = sys.modules["__main__"].enabledeveloper
        self.language = sys.modules["__main__"].language
        self.core = sys.modules["__main__"].core
        self.epg = sys.modules["__main__"].mitvEpg

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


        #
        # Streaming sites
        #
        if mode == 'brightcove':  
            stream_url = self.core.getBrightcove( params('channelid'), params('url') )
        elif mode == 'p2pcast':  
            stream_url = self.core.getP2pcast( params('channelid') )
        elif mode == 'caston':  
            stream_url = self.core.getCastOn( params('channelid') )
        elif mode == 'lw':  
            stream_url = self.core.getLw( params('channelid') )
        elif mode == 'publisher':  
            stream_url = self.core.getPublisher( params('host'), params('channelid') )
        elif mode == 'pxstream':  
            stream_url = self.core.getPxstream( params('url'), params('channelid') )
        elif mode == 'nowlive':  
            stream_url = self.core.getNowLive( params('url'), params('channelid') )
        elif mode == 'widestream':  
            stream_url = self.core.getWideStream( params('url'), params('channelid') )
        elif mode == 'eb':  
            stream_url = self.core.getEb( params('channelid'), params('url') )
        elif mode == 'random':  
            stream_url = self.core.getRandom( params('host'), params('url'), params('referer') )
        elif mode == 'bro.adca.st':  
            stream_url = self.core.getBroadcastSite( params('channelid'), params('url') )
        elif mode == 'radiotime':  
            stream_url = self.core.getRadiotime( params('station') )
        elif mode == 'kastream':  
            stream_url = self.core.getKastream( params('channelid'), params('url') )
        elif mode == 'whostreams':  
            stream_url = self.core.getWhostreams( params('channelid'), params('url') )
        elif mode == 'tltv':  
            stream_url = self.core.getTlTv( params('channelid'), params('url') )
        elif mode == 'limpitv':
            stream_url = self.core.getLimpitv( params('channelid'), params('url') )
        elif mode == 'wstream':
            stream_url = self.core.getWstream( params('channelid'), params('url') )
        elif mode == 'ptv':
            stream_url = self.core.getPremiumtv( params('channelid'), params('url') )
        elif mode == 'cvhls':  
            stream_url = self.core.getCVHLS( params('url') )
        elif mode == 'cvmpd':  
            stream_listitem = self.core.getCVMPD( params('url'), params('url_webapi') )
        
        #
        # Videohosters
        #
        elif mode == 'hqq':  
            stream_url = self.core.getHqq( params('vid') )
        elif mode == 'gamovideo':  
            stream_url = self.core.getGamovideo( params('vid') )
        elif mode == 'streamango':  
            stream_url = self.core.getStreamango( params('vid') )
        elif mode == 'okru':  
            stream_url = self.core.getOkru( params('vid'), params('live') )

        if (stream_listitem == None):
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=stream_url))  
        else:
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, stream_listitem)  


    def addListItem(self, item_params={}):
        item = item_params.get

        # Add TV Channel
        contextmenu = [(self.language(30200), "XBMC.RunPlugin(%s?path=refresh)" % (sys.argv[0], ))]
        image = item('image')
        fanart = os.path.join(self.addon.getAddonInfo("path"), "fanart.jpg")

        #
        # Dont add the 0 channeld (update item) if the user has the latest version
        # ColombiaPlay and ColombiaRadio is the 100 id 
        #
        if item('id') == '0':
            print ("Check for new version")
            if re.search(self.addon.getAddonInfo('version'), item('title')):
                print ("You have the latest version: " + self.addon.getAddonInfo('version'))
            else:
                listitem = self.xbmcgui.ListItem(item('title'))
                listitem.setArt({'icon': image, 'fanart': fanart})
                listitem.setInfo(type='video', infoLabels={'Title': item('title')})

                ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=True)

        elif item('id') == '100':
            print ("Submenu option")
            listitem = self.xbmcgui.ListItem(item('title'))
            listitem.setArt({'icon': image, 'fanart': fanart})
            ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=True)

        else:
            listitem = self.xbmcgui.ListItem(label=item('title'), label2='TV Show')
            listitem.setArt({'icon': image, 'fanart': fanart})
            
            listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
            
            #
            # Get epg data
            #
            now, plot = self.epg.getChannelInfo(item('id'))
            if not now:
                listitem.setInfo('Video', {'Title': item('title'), 'MediaType': 'tvshow', 'Plot': '[B]' + item('title') + '[/B]'})   
            else:
                listitem.setInfo('video',
                {   'title': item('title'),
                    'mediatype': 'tvshow',
                    'plot': '[B]' + item('title') + '[/B][CR][CR]' + plot,
                    'tagline': now["title"] if now["title"] else "",
                    'genre': now["category"] if now["category"] else "",
                    'tag': now["tags"] if now["tags"] else ""
                })
                
            listitem.setProperty('IsPlayable', "true")
            ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=item('url'), listitem=listitem, isFolder=False) 
    