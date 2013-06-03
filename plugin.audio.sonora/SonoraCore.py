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
        self.language = sys.modules["__main__"].language
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

    # Get the Download Links for a song
    def get_download_link(self, id):
        return self.protocol + BASE_URL + '/Media/DownloadMusicByProfile?musicId=' + id + '&profileId=17'
    
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
                    'rating' : usermusic['usermusic']['rating'],
                    'userRate' : usermusic['usermusic']['userRate'],
                    #'id': str(usermusic['usermusic']['id']),
                    'url': self.get_download_link(str(usermusic['usermusic']['id'])),
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
                                'rating' : music1['music']['rating'],
                                'userRate' : music1['music']['userRate'],
                                'url': self.get_download_link(str(music1['music']['id'])),
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
                                'rating' : music1['music']['rating'],
                                'userRate' : music1['music']['userRate'],
                                'url': self.get_download_link(str(music1['music']['id'])),
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
                        'title': genre['genre']['title'] + "(" + self.language(3008) + ")",
                        'image': genre['genre']['image'], 
                        'thumbnail': genre['genre']['image'],
                        'path': "/root/catalog/%s" % (genre['genre']['id'])
                        })
            return genres

    # Creates a list from Ranking artist
    def browse_ranking(self, genreID):
        params = [{'param': 'offset', 'value': 0}, {'param': 'limit', 'value': 50}, {'param': 'GenreID', 'value': genreID}]
        has_child = False
        result = self.__call_sonora__('Ranking/Artists.json', params)
        if (result['artists'] == ''):   
            raise Sonora.SonoraError(1, 'Sonora Fetch Failed' . result['messageText'])
        else:
            # Append all music
            artists = []
            for artist in result['artists']:
                for key in artist:
                    if (key != "count"): 
                        artists.append({'id': key['artist']['id'], 
                            'title': key['artist']['title'],
                            'image': key['artist']['image'], 
                            'thumbnail': key['artist']['image'],
                            'path': "/root/artist/%s" % (key['artist']['id'])
                        })
                        
        return artists

    # Creates a list from the artist CDs.
    def browse_artist(self, id):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'ArtistId', 'value': id}, {'param': 'offset', 'value': 0}, {'param': 'limit', 'value': 50}]
        
        result = self.__call_sonora__('Artists/Cds.json', params)
        if (result['cds'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            cds = []
            for cd in result['cds']:
                for key in cd:
                    if (key != "count"): 
                        for cd1 in key:
                            cds.append({'id': key['cd']['id'], 
                                'title': key['cd']['title'],
                                'image': key['cd']['imageHigher'], 
                                'thumbnail': key['cd']['imageHigher'],
                                'path': "/root/album/%s" % (key['cd']['id'])
                            })
        return cds


    # Creates a list from the albums songs.
    def browse_album(self, id):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'CdId', 'value': id}]
        
        result = self.__call_sonora__('Cds/Musics.json', params)
        if (result['musics'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            musics = []
            for music in result['musics']:
                musics.append({'id': music['music']['id'], 
                    'title': music['music']['title'], 
                    'genre': music['music']['genre'],
                    'image': music['music']['cd']['imageHigher'],
                    'artist': music['music']['artist']['name'],
                    'album': music['music']['cd']['title'],
                    'trackNumber' : music['music']['trackNumber'],
                    'rating' : music['music']['rating'],
                    'userRate' : music['music']['userRate'],
                    'url': self.get_download_link(str(music['music']['id'])),
                    'action': 'play'
                })
        return musics

    # Search a query in music, album and artist
    def search(self, query):
        artist = self.search_artist(query)
        albums = self.search_album(query)
        musics = self.search_music(query)

        results = []
        results.append({'id': "1", 
                        'title': self.language(2003) + " (" + str(len(artist)) + ")",
                        'image': "search", 
                        'thumbnail': "search",
                        'path': "/root/search/artists/%s" % (query)
        
                    })
        
        results.append({'id': "2", 
                        'title': self.language(2004) + " (" + str(len(albums)) + ")",
                        'image': "search", 
                        'thumbnail': "search",
                        'path': "/root/search/albums/%s" % (query)
        
                    })

        results.append({'id': "3", 
                        'title': self.language(2010) + " (" + str(len(musics)) + ")",
                        'image': "search", 
                        'thumbnail': "search",
                        'path': "/root/search/musics/%s" % (query)
        
                    })

        return results

    # Search a artist based in query
    def search_artist(self, query):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'TextSearch', 'value': query}, {'param': 'offset', 'value': 0}, {'param': 'limit', 'value': 50}]
        
        result = self.__call_sonora__('Search/Artists.json', params)
        if (result['artists'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            artists = []
            for artist in result['artists']:
                for key in artist:
                    if (key != "count"): 
                        artists.append({'id': key['artist']['id'], 
                            'title': key['artist']['title'],
                            'image': key['artist']['image'], 
                            'thumbnail': key['artist']['image'],
                            'path': "/root/artist/%s" % (key['artist']['id'])
                        })
        return artists

    # Search an album based in query
    def search_album(self, query):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'TextSearch', 'value': query}, {'param': 'offset', 'value': 0}, {'param': 'limit', 'value': 50}]
        
        result = self.__call_sonora__('Search/Cds.json', params)
        if (result['cds'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj

        else:
            # Append all music
            cds = []
            for cd in result['cds']:
                for key in cd:
                    if (key != "count"): 
                        for cd1 in key:
                            cds.append({'id': key['cd']['id'], 
                                'title': key['cd']['title'],
                                'image': key['cd']['imageHigher'], 
                                'thumbnail': key['cd']['imageHigher'],
                                'path': "/root/album/%s" % (key['cd']['id'])
                            })
        return cds

    # Search a music based in query
    def search_music(self, query):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'TextSearch', 'value': query}, {'param': 'offset', 'value': 0}, {'param': 'limit', 'value': 50}]
        
        result = self.__call_sonora__('Search/Musics.json', params)
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
                                'rating' : music1['music']['rating'],
                                'userRate' : music1['music']['userRate'],
                                'url': self.get_download_link(str(music1['music']['id'])),
                                'action': 'play'
                            })
        return musics


    # Like a song in the favorites playlist
    def like_music(self, musicid):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'musicid', 'value': musicid}]
        
        result = self.__call_sonora__('User/Like.json', params)
        if (result['response'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj
        else:
            ret_obj = {"status": 200, "content": "", "error": 0}
            
        return ret_obj


    # Dislike a song in the favorites playlist
    def dislike_music(self, musicid):
        ret_obj = {"status": 500, "content": "", "error": 0}
        params = [{'param': 'musicid', 'value': musicid}]
        
        result = self.__call_sonora__('User/dislike.json', params)
        if (result['response'] == ''):    
            ret_obj["content"] = 'Sonora Fetch Failed' . result['messageText']
            raise ret_obj
        else:
            ret_obj = {"status": 200, "content": "", "error": 0}

        return ret_obj