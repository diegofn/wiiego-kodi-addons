#/*
# *
# * ColombiaTV: ColombiaTV add-on for XBMC.
# *
# * Copyright (C) 2013-2016 Wiiego
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
import cgi
import gzip
import json
from StringIO import StringIO

import ConfigParser
import xml.dom.minidom as minidom

# ERRORCODES:
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

# Base URL for all querys. 
#http://tvi.une.net.co/wsLiveChannelsLoad/live_channels.php?token=07b95eb4ba4fe65ba0c68fb304bc1769
#http://uneapple-i.akamaihd.net/hls/live/205013/grupoune_st4@205013/master.m3u8
#http://tvi.une.net.co/upload/images/logos/110x70/1025.png
BASE_URL='dl.dropboxusercontent.com'
CHANNEL_URL='/u/30021391/XBMC/'


class ColombiaTVCore():
    # Define the global variables for ColombiaTV
    def __init__(self, instanceId=10, platformId=4, version=10):
        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        self.xbmcplugin = sys.modules["__main__"].xbmcplugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        urllib2.install_opener(sys.modules["__main__"].opener)

        self.url = "https://" + BASE_URL + CHANNEL_URL + 'channels.json'

    # Return the URL from TV Channel
    def getChannelList(self):
        request = urllib2.Request(self.url)
        requesturl = urllib2.urlopen(request)
        result = simplejson.load(requesturl)
        requesturl.close()

        if self.enabledebug == True:
            print (result['ColombiaTV'])
        return result['ColombiaTV']


    # Brightcove Plugin
    def demunge(self, munge):
        try:
            munge = urllib.unquote_plus(munge).decode(UTF8)
        except:
            pass
        return munge

    def getBrightcoveRequest(self, url):
        print ("getRequest URL:" + str(url))

        USER_AGENT = 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_2 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8H7 Safari/6533.18.5'
        UTF8          = 'utf-8'
        headers = {'User-Agent':USER_AGENT, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8', 'Cookie':'hide_ce=true'} 
        req = urllib2.Request(url.encode(UTF8), None, headers)

        try:
            response = urllib2.urlopen(req)
            if response.info().getheader('Content-Encoding') == 'gzip':
                print ("Content Encoding == gzip")
                buf = StringIO( response.read() )
                f = gzip.GzipFile(fileobj=buf)
                link1 = f.read()
            else:
                link1=response.read()
        except:
            link1 = ""

        link1 = str(link1).replace('\n','')
        return(link1)

    def getBrightcove (self, video_content_id):
        print ("VideoContent id: " + video_content_id)

        url = "https://secure.brightcove.com/services/viewer/htmlFederated?&width=859&height=482&flashID=myExperience-myExperience-1&bgcolor=%23FFFFFF&playerID=3950496857001&playerKey=AQ~~%2CAAADexCiUfE~%2CJftGHB2I9gVI2XEYYJLrw_JktV22Q9KB&isVid=true&isUI=true&dynamicStreaming=true&%40videoPlayer=" + video_content_id + "&secureConnections=true&secureHTMLConnections=true"
        html = self.getBrightcoveRequest(url)

        a = re.compile('experienceJSON = (.+?)\};').search(html).group(1)
        a = a+'}'
        a = json.loads(a)
        try:
            b = a['data']['programmedContent']['videoPlayer']['mediaDTO']['IOSRenditions']
            u =''
            rate = 0
            for c in b:
                if c['encodingRate'] > rate:
                   rate = c['encodingRate']
                   u = c['defaultURL']
            b = a['data']['programmedContent']['videoPlayer']['mediaDTO']['renditions']
            for c in b:
                if c['encodingRate'] > rate:
                   rate = c['encodingRate']
                   u = c['defaultURL']
            if rate == 0:
                try:
                    u = a['data']['programmedContent']['videoPlayer']['mediaDTO']['FLVFullLengthURL']
                    print ("Final URL: " + u);
                except:
                    u = ''

            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=u))
        
        except:
            pass
        