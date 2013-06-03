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

import sys
import urllib
import os
import re

class SonoraNavigation():
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
        self.login = sys.modules["__main__"].login
        
        # Main Menu Structure
        #     label                         , path                          , thumbnail                     ,  login                ,feed / action
        self.categories = (
            {'title':self.language(2002)    ,'path':"/root/favorites"       , 'thumbnail':"favorites"       , 'login':"true" ,      'user_feed':"favorites" },
            {'title':self.language(2005)    ,'path':"/root/playlist"        , 'thumbnail':"playlist"        , 'login':"true" ,      'user_feed':"playlist",     'folder':"true"},
            {'title':self.language(2006)    ,'path':"/root/featured"        , 'thumbnail':"featured"        , 'login':"false",      'feed':"feed_featured" },
            {'title':self.language(2007)    ,'path':"/root/catalog/0/0"    , 'thumbnail':"catalog"         , 'login':"false" ,     'feed':"feed_catalog" },
            {'title':self.language(2008)    ,'path':"/root/ranking"         , 'thumbnail':"ranking"         , 'login':"false" ,     'feed':"feed_ranking" },
            {'title':self.language(2009)    ,'path':"/root/search"          , 'thumbnail':"search"          , 'login':"false" ,     'feed':"search",         'folder':'true' },
            )

    def listMenu(self, params={}):
        self.common.log(repr(params), 1)
        get = params.get

        path = get("path", "/root")
        if (path == "/root"):
            for category in self.categories:
                self.addListItem(params, category)
        else:
            self.list(params)

        self.xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)
        self.common.log("Done", 5)


    def executeAction(self, params={}):
        self.common.log(params, 3)
        get = params.get

        action = get("action")

        if (action == "play"):
            id = get("id")
            url =  self.core.get_download_link(id)
            
            player_type = self.xbmc.PLAYER_CORE_DVDPLAYER
            xbmcPlayer = self.xbmc.Player(player_type)

            # Play the file 
            xbmcPlayer.play(url)
        elif (action == "like"):
            musicid = get("musicid")
            response = self.core.like_music(musicid)

        elif (action == "dislike"):
            musicid = get("musicid")
            response = self.core.dislike_music(musicid)

        self.common.log("Done", 5)

    def list(self, params={}):
        self.common.log(repr(params), 1)
        get = params.get

        path = get("path")
        if (path.find("favorites") > -1):
            results = self.core.browse_favorite_songs()
            for result in results:
                self.addListItem(params, result)

        elif (path.find("featured") > -1): 
            match = re.match('.*featured/(.*)', path)
            if not match:
                results = self.core.browse_featured_category()
            else:
                results = self.core.browse_music_list(match.group(1), mediaType=50)

            for result in results:
                self.addListItem(params, result)

        elif (path.find("playlist") > -1): 
            match = re.match('.*playlist/(.*)', path)
            if not match:
                results = self.core.browse_playlist_category()
            else:
                results = self.core.browse_playlist(match.group(1))

            for result in results:
                self.addListItem(params, result)
        
        elif (path.find("catalog") > -1): 
            match = re.match('.*catalog/(.*)/(.*)', path)
            if not match:
                matchGroup = re.match('.*catalog/(.*)', path)
                results = self.core.browse_music_list(matchGroup.group(1), mediaType=56)
            else:
                results = self.core.browse_catalog(match.group(1), match.group(2))

            for result in results:
                self.addListItem(params, result)

        elif (path.find("ranking") > -1):
            results = self.core.browse_ranking(genreID=-1)
            for result in results:
                self.addListItem(params, result)

        elif (path.find("search") > -1):
            match_music = re.match('.*search/musics/(.*)', path)
            match_artist = re.match('.*search/artists/(.*)', path)
            match_album = re.match('.*search/albums/(.*)', path)

            if match_music:
                results = self.core.search_music(match_music.group(1))
           
            elif match_artist:
                results = self.core.search_artist(match_artist.group(1))  
            
            elif match_album:
                results = self.core.search_album(match_album.group(1))  
                
            else:
                query = self.common.getUserInput(self.language(3002), '')    
                if len(query) > 0:
                    results = self.core.search(query)

            for result in results:
                self.addListItem(params, result)

        elif (path.find("artist") > -1): 
            match = re.match('.*artist/(.*)', path)
            if match:
                results = self.core.browse_artist(match.group(1))

            for result in results:
                self.addListItem(params, result)

        elif (path.find("album") > -1):
            match = re.match('.*album/(.*)', path)
            if match:
                results = self.core.browse_album(match.group(1))

            for result in results:
                self.addListItem(params, result)

        else:
            print (get("path"))

    def addListItem(self, params={}, item_params={}):
        item = item_params.get

        if (item("action")):
            # Add a Play Element
            if (item("action") == "play"):
                # Add a Music Element
                contextmenu = []
                if (item('userRate') == 0):
                    contextmenu.append ( (self.language(3009), "XBMC.RunPlugin(%s?action=like&musicid=%s)" % ( sys.argv[0], item('id'))) )
                else:
                    contextmenu.append ( (self.language(3010), "XBMC.RunPlugin(%s?action=dislike&musicid=%s)" % ( sys.argv[0], item('id'))) )
                
                image = item('image')
                fanart = os.path.join(self.settings.getAddonInfo("path"), "fanart.jpg")

                listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
                listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
                listitem.setProperty("fanart_image", fanart)
                listitem.setInfo('Music', {'Title': item('title'), 'Artist': item('artist'), 'Album': item('album'), 'Genre': item('genre'), 'Comment': '', 'Tracknumber': item('trackNumber'), 'Rating': item('rating')})
                listitem.setProperty('IsPlayable', "true")
                
                # WISH. Play mp4 with the DVD Player
                #url = "%s?action=play&id=%s" % (sys.argv[0], item('id'))
                url = item('url')
                ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

            else:
                url = "%s?path=%s&" % (sys.argv[0], item("path"))
                url += 'action=' + item("action")
        else:
            # Add a Directory or Category
            contextmenu = [(self.language(3001), "XBMC.RunPlugin(%s?path=refresh)" % (sys.argv[0], ))]

            if (item("thumbnail").find("http") > -1):
                image = item("thumbnail")
            else:
                image = os.path.join(self.settings.getAddonInfo("path"), "resources/images/" + item("thumbnail") + ".png")

            fanart = os.path.join(self.settings.getAddonInfo("path"), "fanart.jpg")
            listitem = self.xbmcgui.ListItem(item('title'), iconImage=image, thumbnailImage=image)
            listitem.addContextMenuItems(items=contextmenu, replaceItems=True)
            listitem.setProperty("fanart_image", fanart)
            url = "%s?path=%s&" % (sys.argv[0], item("path"))
            ok = self.xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)
            
        self.common.log("Done", 5)
