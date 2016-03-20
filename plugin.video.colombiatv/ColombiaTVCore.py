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
import base64
from StringIO import StringIO
import jsUnwiser

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

    #
    # Brightcove support
    #
    def demunge(self, munge):
        try:
            munge = urllib.unquote_plus(munge).decode(UTF8)
        except:
            pass
        return munge

    def getRequest(self, url):
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

    def getBrightcove (self, videoContentId):
        print ("VideoContent id: " + videoContentId)

        url = "https://secure.brightcove.com/services/viewer/htmlFederated?&width=859&height=482&flashID=myExperience-myExperience-1&bgcolor=%23FFFFFF&playerID=3950496857001&playerKey=AQ~~%2CAAADexCiUfE~%2CJftGHB2I9gVI2XEYYJLrw_JktV22Q9KB&isVid=true&isUI=true&dynamicStreaming=true&%40videoPlayer=" + videoContentId + "&secureConnections=true&secureHTMLConnections=true"
        html = self.getRequest(url)

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
    
    #
    # Fog support
    #    
    def getFog (self, referUrl, videoContentId):
        try:
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)

            html = self.getRequest(urllib.unquote(referUrl)) 

            # Get the wmsAuthSign
            wmsAuthCode = ""
            m = re.compile('(\w+)\.join\(\"\"\) \+ document\.getElementById\(\"(\w+)\"\)\.innerHTML').search(html)
            first = m.group(1)
            last = m.group(2)
            
            # first part
            m = re.compile (first + ' = \[\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\",\"(\w+)\"\]').search(html)
            if m:
                for e in m.groups():
                    wmsAuthCode = wmsAuthCode + e 
            else:
                print ("First parse error")

            # last part
            m = re.compile ('id\=' + last + '>(\S{48})<\/span>').search(html)
            if m:
                wmsAuthCode = wmsAuthCode + m.group(1)
            else:
                print ("Last parse error")


            # Parse the final URL
            u = "http://62.210.75.76:8081/hlslive/" + videoContentId + "/playlist.m3u8?wmsAuthSign=" + wmsAuthCode
            print ("Final URL: " + u);
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=u))  
        except:
            pass

    #
    # p2pcast support
    #    
    def getRequestP2pcast (self, url, referUrl, userAgent, xRequestedWith=""):
        UTF8 = 'utf-8'
        headers = {'User-Agent':userAgent, 'Referer':referUrl, 'X-Requested-With': xRequestedWith, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8', 'Cookie':'hide_ce=true'} 
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


    def getP2pcast (self, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the decodeURL
            print ("VideoContent id: " + videoContentId)
            html = self.getRequestP2pcast("http://p2pcast.tech/stream.php?id=" + videoContentId, "http://p2pcast.tech/stream.php?id=" + videoContentId + "&osr=0&p2p=0&stretching=uniform", USER_AGENT)
            m = re.compile('murl = "(.*?)"').search(html)
            decodedURL = base64.b64decode(m.group(1))
            print ("decodedURL: " + decodedURL)
                        
            # Get the token
            html = self.getRequestP2pcast("http://p2pcast.tech/getTok.php", "http://p2pcast.tech/stream.php?id=" + videoContentId, USER_AGENT, "XMLHttpRequest")
            m = re.compile('"token":"(.*?)"').search(html)
            token = m.group(1)
            print ("token: " + token)

            # Get the URL Enconded Link
            urlEncodedLink = urllib.quote_plus(decodedURL + token + "|Referer=http://cdn.p2pcast.tech/jwplayer.flash.swf&User-Agent=" + USER_AGENT)

            # Parse the final URL
            u = "plugin://plugin.video.f4mTester/?streamtype=HLS&amp;url=" + urlEncodedLink
            print ("Final URL: " + u);
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=u))  
        except:
            pass

    #
    # CastOn.tv support
    #
    def getCastOn (self, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the unWiser content
            print ("VideoContent id: " + videoContentId)
            html = self.getRequestP2pcast("http://www.caston.tv/player.php?id=" + videoContentId, "http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390", USER_AGENT)
            m = re.compile('unescape\(\'(.*)\'\)\);').search(html)
            unWiser = jsUnwiser.JsUnwiser()
            unWiserContent = unWiser.unwiseAll(urllib.unquote(m.group(1)))
                        
            # Get the decodedURL
            m = re.compile('file:"(.*?)"').search(unWiserContent)
            decodedURL = m.group(1)
            print ("decodedURL: " + decodedURL)

            # Get the token
            html = self.getRequestP2pcast("http://www.caston.tv/ss.php", "http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390", USER_AGENT, "XMLHttpRequest")
            m = re.compile('"(.*?)"').search(html)
            token = m.group(1)
            print ("token: " + token)

            # Get the URL Enconded Link
            urlEncodedLink = urllib.quote_plus(decodedURL + token + "|Referer=http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390&User-Agent=" + USER_AGENT)

            # Parse the final URL
            u = "plugin://plugin.video.f4mTester/?streamtype=HLS&amp;url=" + urlEncodedLink
            print ("Final URL: " + u);
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=u))  
        except:
            pass

    #
    # mips.tv support
    #
    def getMips (self, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"

        try:
            # Get the stream IP Address
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest("http://cdn.mipspublisher.com:1935/loadbalancer")
            m = re.compile('redirect=(.*)').search(html)
            ipAddress = m.group(1)
            print ("ipAddress: " + ipAddress)
                                    
            # Get the m3u8 URL
            html = self.getRequestP2pcast("http://www.mips.tv/membedplayer/" + videoContentId + "/1/500/400", "http://www.mips.tv", USER_AGENT)
            m = re.compile('ea \+ \"(.*?)\"').search(html)
            m3u8Address = m.group(1)
            print ("m3u8Address: " + m3u8Address)

            # Parse the final URL
            u = "http://" + ipAddress + m3u8Address
            print ("Final URL: " + u);
            self.xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, self.xbmcgui.ListItem(path=u))  
        except:
            pass
