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
import os

import simplejson
import urllib
import urllib2
import cookielib
import subprocess
import re

import ConfigParser
import xml.dom.minidom as minidom

# ERRORCODES:
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

# Base URL for all querys. 
BASE_URL='webservices.sonora.terra.com.br/'

class SonoraCore():
    # Init the Sonora Object. Define URL standar parameters
    def __init__(self, instanceId=10, platformId=4, version=10):
        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        urllib2.install_opener(sys.modules["__main__"].opener)

        self.global_params = []
        self.global_params.append({'param': 'instanceId', 'value': instanceId})
        self.global_params.append({'param': 'platformId', 'value': platformId})
        self.global_params.append({'param': 'version', 'value': version})
        self.protocol = "http://"
        self.is_authenticated = False


    # Return the URL with all parameters
    def __add_params_to_url__(self, method, fnparams=None, addrender=True, addserial=True):
        params = {}

        for param in self.global_params:
            if (param['param'] == 'render' and addrender == False):
                pass
            elif (param['param'] == 'serial' and addrender == False):
                pass
            elif (param['value']):
                params[param['param']] = param['value']

        for param in fnparams:
            if (param['value']):
                params[param['param']] = param['value']

        url = '%s%s%s?%s' %(self.protocol, BASE_URL, method, urllib.urlencode(params))
        if self.enabledebug == True:
            print '[Sonora] URL: %s' % url 
        return url


    # Call the WebAPI 
    def __call_sonora__(self, method, params=None):
        url = self.__add_params_to_url__(method, params)
        req = urllib2.Request(url)
        f = urllib2.urlopen(req)
        result = simplejson.load(f)
        f.close()
        return result


    # Define Sonora Country.
    def __set_country__(self):
        params = []
        result = self.__call_sonora__('GeoLocation/ContryCodeByIP.json', params)


    # Verifies credentials associated with a Sonora account.
    def account_auth(self, username, password):
        self.__set_country__()
        params = [{'param': 'username', 'value': username}, {'param': 'password', 'value': password}]
        result = self.__call_sonora__('User/Login.json', params)
        if (result['loggedIn'] != True):
            result = 'Account authentication failed: ' . result['messageText']
            status = 303
            self.settings.setSettings()
        else:
            self.is_authenticated = True
            result = result['loggedIn']
            status = 200

        return (result, status)


    # Creates a list from the favorite user songs.
    def browse_favorite_songs(self):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = []
        
        result = self.__call_sonora__('User/MyMusics.json', params)
        if (result['usermusics'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            usermusics = []
            for usermusic in result['usermusics']:
                usermusics.append({'id': usermusic['usermusic']['id'], 
                    'title': usermusic['usermusic']['title'], 
                    'genre': usermusic['usermusic']['genre'],
                    'image': usermusic['usermusic']['cd']['imageHigher'],
                    'artist': usermusic['usermusic']['artist']['name'],
                    'album': usermusic['usermusic']['cd']['title'],
                    'trackNumber' : usermusic['usermusic']['trackNumber'],
                    'url': self.protocol + BASE_URL + '/Media/DownloadMusicByProfile?musicId=' + str(usermusic['usermusic']['id']) + '&profileId=17',
                    'action': 'play'
                })
        return usermusics


    # Creates a list from the featured category
    def browse_featured_category(self):
        params = []
        result = self.__call_sonora__('Radios/Highlights.json', params)
        if (result['radios'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            radios = []
            for radio in result['radios']:
                radios.append({'id': radio['radio']['id'], 
                    'title': radio['radio']['title'],
                    'image': radio['radio']['image'],
                    'thumbnail': radio['radio']['image'],
                    'path': "/root/featured/%s" % (radio['radio']['id'])
                    })
            
            return radios
            
    # Creates a list from the Music List
    def browse_music_list(self, id, mediaType):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'mediaType', 'value': mediaType}, {'param': 'id', 'value': id}]
        
        result = self.__call_sonora__('Media/MusicList.json', params)
        if (result['musics'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            musics = []
            for music in result['musics']:
                for key in music:
                    if (key != "count"): 
                        for music1 in key:
                            musics.append({'id': music1['music']['id'], 
                                'title': music1['music']['title'], 
                                'genre': music1['music']['genre'],
                                'image': music1['music']['cd']['imageHigher'],
                                'artist': music1['music']['artist']['name'],
                                'album': music1['music']['cd']['title'],
                                'trackNumber' : music1['music']['trackNumber'],
                                'url': self.protocol + BASE_URL + '/Media/DownloadMusicByProfile?musicId=' + str(music1['music']['id']) + '&profileId=17',
                                'action': 'play'
                            })
        return musics

    # Creates a list from the favorite user playlist
    def browse_playlist_category(self):
        params = []
        result = self.__call_sonora__('User/MyPlaylists.json', params)
        if (result['myplaylists'] == ''):   
            raise Sonora.SonoraError(1, 'Sonora Fetch Failed' . result['messageText'])
        else:
            # Append all music
            playlists = []
            for playlist in result['myplaylists']:
                playlists.append({'id': playlist['playlist']['id'], 
                    'title': playlist['playlist']['title'],
                    'image': '', # WISH Standard playlist image
                    'thumbnail': '',
                    'path': "/root/playlist/%s" % (playlist['playlist']['id'])
                    })
            
            return playlists

    # Creates a list from the favorite user playlist
    def browse_playlist(self, id):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'limit', 'value': 150}, {'param': 'playlistId', 'value': id}]
        
        result = self.__call_sonora__('Playlist/Musics.json', params)
        if (result['musics'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            musics = []
            for music in result['musics']:
                for key in music:
                    if (key != "count"): 
                        for music1 in key:
                            musics.append({'id': music1['music']['id'], 
                                'title': music1['music']['title'], 
                                'genre': music1['music']['genre'],
                                'image': music1['music']['cd']['imageHigher'],
                                'artist': music1['music']['artist']['name'],
                                'album': music1['music']['cd']['title'],
                                'trackNumber' : music1['music']['trackNumber'],
                                'url': self.protocol + BASE_URL + '/Media/DownloadMusicByProfile?musicId=' + str(music1['music']['id']) + '&profileId=17',
                                'action': 'play'
                            })
        return musics

    # Creates a list from the favorite user playlist
    def browse_catalog(self, id, parent):
        params = []
        has_child = False
        result = self.__call_sonora__('Genres/List.json', params)
        if (result['genres'] == ''):   
            raise Sonora.SonoraError(1, 'Sonora Fetch Failed' . result['messageText'])
        else:
            # Append all music
            genres = []
            for genre in result['genres']:
                print ("Parent: " + str(genre['genre']['parent']))
                print ("id: " + str(id))
                print ("Genre: " + str(genre['genre']['id']))

                has_child = False
                if (str(genre['genre']['parent']) == str(id)):
                    # Seek is genre has childs
                    for genre_childs in result['genres']:
                        if (str(genre['genre']['id']) == str(genre_childs['genre']['parent'])):
                            has_child = True
                            
                    if (has_child):
                        genres.append({'id': genre['genre']['id'], 
                            'title': genre['genre']['title'],
                            'image': genre['genre']['image'], 
                            'thumbnail': genre['genre']['image'],
                            'path': "/root/catalog/%s/%s" % (genre['genre']['id'], parent)
                            })
                    else:
                        # Add the category
                        genres.append({'id': genre['genre']['id'], 
                            'title': genre['genre']['title'],
                            'image': genre['genre']['image'], 
                            'thumbnail': genre['genre']['image'],
                            'path': "/root/catalog/%s" % (genre['genre']['id'])
                            })

                # Add the main category
                elif (str(genre['genre']['id']) == str(id) and str(id) != "0"):
                    genres.append({'id': genre['genre']['id'], 
                        'title': genre['genre']['title'] + " (All)",
                        'image': genre['genre']['image'], 
                        'thumbnail': genre['genre']['image'],
                        'path': "/root/catalog/%s" % (genre['genre']['id'])
                        })
            return genres
