#/*
# *
# * ColombiaTV: ColombiaTV add-on for Kodi.
# *
# * Copyleft 2013-2017 Wiiego
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
import hqqresolver
import ssl
import xbmc

import ConfigParser
import xml.dom.minidom as minidom

# ERRORCODES:
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

# Base URL for all querys. 
DROPBOX_BASE_URL='dl.dropboxusercontent.com'
GITHUB_BASE_URL='gist.githubusercontent.com'

class ColombiaTVCore():
    # Define the global variables for ColombiaTV
    def __init__(self, instanceId=10, platformId=4, version=10):
        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        urllib2.install_opener(sys.modules["__main__"].opener)

        # SSL context since Kodi Krypton version
        try:
           import ssl
           ssl._create_default_https_context = ssl._create_unverified_context
        except:
           pass

        CHANNEL_URL = base64.b64decode("L3UvMzAwMjEzOTEvWEJNQy9jaGFubmVscy5qc29u")
        self.url = "https://" + DROPBOX_BASE_URL + CHANNEL_URL

        CHANNEL_URL_BACKUP = base64.b64decode("L2RpZWdvZm4vYjAwMzYyMjc4YjFjYTE3MWIyN2ViNDBiZDdjMmQ1ZTQvcmF3LzhhMDQ5OTEzOWIzMTI5ZmE0MGZkOTliY2VkZTA4NzAwYzE3NWI5YzYv")
        self.urlbackup = "https://" + GITHUB_BASE_URL + CHANNEL_URL_BACKUP + "channels.json"

    # Return the URL from TV Channel
    def getChannelList(self):
        try:
            request = urllib2.Request(self.url)
            requesturl = urllib2.urlopen(request)

            result = simplejson.load(requesturl)
            requesturl.close()

            if self.enabledebug == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']
        except:
            request = urllib2.Request(self.urlbackup)
            requesturl = urllib2.urlopen(request)

            result = simplejson.load(requesturl)
            requesturl.close()

            if self.enabledebug == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']
        

    # Return the Show List 
    def getShowList(self, show):
        show_url = "https://" + DROPBOX_BASE_URL + base64.b64decode(urllib.unquote(show))
        request = urllib2.Request(show_url)
        requesturl = urllib2.urlopen(request)

        result = simplejson.load(requesturl)
        requesturl.close()

        if self.enabledebug == True:
            print (result['ColombiaPlay'])
        return result['ColombiaPlay']

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
        request = urllib2.Request(url.encode(UTF8), None, headers)

        try:
            response = urllib2.urlopen(request)
                
            if response.info().getheader('Content-Encoding') == 'gzip':
                print ("Content Encoding == gzip")
                buf = StringIO( response.read() )
                f = gzip.GzipFile(fileobj=buf)
                link1 = f.read()
            else:
                link1=response.read()
        except Exception as e:
            link1 = ""

        link1 = str(link1).replace('\n','')
        return(link1)

    def getBrightcove (self, videoContentId, referUrl):
        print ("VideoContent id: " + videoContentId)

        USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/13G34 Safari/601.1.46"
        url = "http://c.brightcove.com/services/viewer/htmlFederated?&width=640&height=360&flashID=myExperience4042799614001&identifierClassName=BrightcoveExperienceID_9889&bgcolor=%23FFFFFF&wmode=transparent&playerID=4109933993001&playerKey=AQ~~%2CAAADexCiPmk~%2Chd5maXWwxzDmaeRpSVEvmO9M4jcJ6Ow3&isVid=true&isUI=true&dynamicStreaming=true&%40videoPlayer=" + videoContentId + "&includeAPI=true&templateLoadHandler=BCL.onTemplateLoad&templateReadyHandler=BCL.onTemplateReady&autoStart=&debuggerID=&startTime=1474130689252&refURL=not%20available"
        html = self.getRequestP2pcast(url, referUrl, USER_AGENT)
        
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
                    print ("Final URL: " + u)
                except:
                    u = ''

            return u
        
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
            print (html)
            m = re.compile (first + ' = \[\"(.*?)\"\]').search(html)
            if m:
                wmsAuthCode = m.group(1).replace('\",\"', '')
            else:
                print ("First parse error")

            # last part
            m = re.compile ('id\=' + last + '>(.*?)<\/span>').search(html)
            if m:
                wmsAuthCode = wmsAuthCode + m.group(1)
            else:
                print ("Last parse error")
            
            print "wmsAuthCode: " + wmsAuthCode

            # Get the URL Path
            m = re.compile ('{return\(\[\"h(.*?)\"\].join').search(html)
            if m:
                streamPath = "h" + ( m.group(1).replace('\",\"', '').replace('\\/', '/') )
            else:
                print ("Last parse error")

            # Parse the final URL
            u = streamPath + wmsAuthCode
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # p2pcast support
    #    
    def getRequestP2pcast (self, url, referUrl, userAgent, xRequestedWith=""):
        UTF8 = 'utf-8'
        headers = {'User-Agent':userAgent, 'Referer':referUrl, 'X-Requested-With': xRequestedWith, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8', 'Cookie':'hide_ce=true'} 
        request = urllib2.Request(url.encode(UTF8), None, headers)

        try:
            response = urllib2.urlopen(request)
            
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

    #  
    # NowLive support
    #
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
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # NowLive support
    #
    def getNowLive (self, referUrl, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the decodeURL
            print ("VideoContent id: " + videoContentId)
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            html = self.getRequestP2pcast("http://nowlive.pw/stream.php?id=" + videoContentId + "&width=680&height=380&stretching=uniform&p=1", urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('curl = "(.*?)"').search(html)
            decodedURL = base64.b64decode(m.group(1))
            print ("decodedURL: " + decodedURL)
                        
            # Get the token
            html = self.getRequestP2pcast("http://nowlive.pw/getToken.php", "http://nowlive.pw/stream.php?id=" + videoContentId, USER_AGENT, "XMLHttpRequest")
            m = re.compile('"token":"(.*?)"').search(html)
            token = m.group(1)
            print ("token: " + token)

            # Parse the final URL
            u = decodedURL + token + "|Referer=http://nowlive.pw/stream.php?id=" + videoContentId + "&width=680&height=380&stretching=uniform&p=1&User-Agent=" + USER_AGENT
            print ("Final URL: " + u)
            return u
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
            html = self.getRequestP2pcast("http://www.caston.tv/sssss.php", "http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390", USER_AGENT, "XMLHttpRequest")
            m = re.compile('"(.*?)".*",(.*?)]').search(html)
            token = m.group(1)
            element = m.group(2)
            print ("token: " + token)
            print ("element: " + element)

            # Get the URL Enconded Link
            urlEncodedLink = urllib.quote_plus(decodedURL + token + "&e=" + element + "|Referer=http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390&User-Agent=" + USER_AGENT)

            # Parse the final URL
            u = "plugin://plugin.video.f4mTester/?streamtype=HLS&amp;url=" + urlEncodedLink
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # mips.tv and similar sites support
    #
    def getPublisher (self, host, videoContentId):
        #
        # Global variables
        #
        CHANNEL_URL = ""
        STREAM_IP = ""
        USER_AGENT = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"

        if host == "mips":
            STREAM_IP = "http://cdn.mipspublisher.com:1935/loadbalancer"
            CHANNEL_URL = "http://www.mips.tv/membedplayer/" + videoContentId + "/1/500/400"
            REFERER = "http://www.mips.tv"
        elif host == "streamify":
            STREAM_IP = "http://www.streamifypublisher.com:1935/loadbalancer?22097*"
            CHANNEL_URL = "http://www.streamifyplayer.com/membedplayer/" + videoContentId + "/1/620/380"
            REFERER = "http://www.streamifyplayer.com"
        elif host == "liveflash":
            STREAM_IP = "http://www.liveflashpublisher.com:1935/loadbalancer?24694"
            CHANNEL_URL = "http://www.liveflashplayer.net/membedplayer/" + videoContentId + "/1/620/380"
            REFERER = "http://www.liveflashplayer.net"
        elif host == "janjua":
            STREAM_IP = "http://www.janjuapublisher.com:1935/loadbalancer?58743"
            CHANNEL_URL = "http://www.janjuaplayer.com/membedplayer/" + videoContentId + "/1/620/380"
            REFERER = "http://www.janjuaplayer.com"
        elif host == "zony":
            STREAM_IP = "http://cdn.pubzony.com:1935/loadbalancer"
            CHANNEL_URL = "http://www.zony.tv/membedplayer/" + videoContentId + "/1/620/380"
            REFERER = "http://www.zony.tv"

        try:
            # Get the stream IP Address
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest(STREAM_IP)
            m = re.compile('redirect=(.*)').search(html)
            ipAddress = m.group(1)
            print ("ipAddress: " + ipAddress)
                                    
            # Get the m3u8 URL
            html = self.getRequestP2pcast(CHANNEL_URL, REFERER, USER_AGENT)
            m = re.compile('ea \+ \"(.*?)\"').search(html)
            m3u8Address = m.group(1)
            print ("m3u8Address: " + m3u8Address)

            # Parse the final URL
            u = "http://" + ipAddress + m3u8Address
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # lw.ml support
    #
    def getLw (self, videoContentId):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2969.0 Safari/537.36"

        try:
            # Get the stream IP Address
            print ("VideoContent id: " + videoContentId)            
            html = self.getRequest("http://latino-webtv.com/embed/canales.php?ch=" + videoContentId + "&sd=si")

            # Find and decode the URL
            m = re.compile('file: "(.*?)",').search(html)
            streamUrl = m.group(1)
                                    
            # Parse the final URL
            u = streamUrl + "|Referer=http://latino-webtv.com/embed/canales.php?ch=" + videoContentId + "&sd=si" + "&User-Agent=" + USER_AGENT
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # pxstream.tv support
    #
    def getPxstream (self, referUrl, videoContentId):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2727.0 Safari/537.36"

        try:
            # Get the stream IP Address
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)
            html = self.getRequestP2pcast("http://pxstream.tv/embedrouter.php?file=" + videoContentId + "&width=680&height=380&jwplayer=flash", urllib.unquote(referUrl), USER_AGENT)
                        
            # Find and decode the URL
            m = re.compile('file: "(.*?)"').search(html)
            streamUrl = m.group(1)
            print ("streamUrl: " + streamUrl)
                                    
            # Parse the final URL
            u = streamUrl 
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # HQQ Support
    #
    def getHqq (self, vid):
        try:
            # Get the stream URL
            print ("VideoContent id: " + vid)
            hqqvidresolver = hqqresolver.hqqResolver()
                                    
            # Parse the final URL
            u = hqqvidresolver.resolve(vid)
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # eb support
    #
    def getEb (self, channelId, referUrl):
        try:
            USER_AGENT = "THEKING"
            print "URL: " + base64.b64decode(urllib.unquote(referUrl))
            html = self.getRequestP2pcast(base64.b64decode(urllib.unquote(referUrl)), "", USER_AGENT) 
            
            # Get the URL Path
            m = re.compile ("([^:]*)\/" + channelId + "\/(.*?)<\/link>").search(html)
            if m:
                streamPath = "http:" + m.group(1) + "/" + channelId + "/" + m.group(2)
            else:
                print ("Last parse error")

            # Parse the final URL
            u = streamPath
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # Random support
    #
    def getRandom (self, host, referUrl):
        if host == "ssh101":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
                print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
                html = self.getRequestP2pcast(urllib.unquote(referUrl), "", USER_AGENT) 

                # Get the URL Path
                m = re.compile ("'file': '(.*?)',").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("Last parse error")

                # Parse the final URL
                u = streamPath
                print ("Final URL: " + u)
                return u
            except:
                pass

        elif host == "janjua":
            try:
                print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
                html = self.getRequest(urllib.unquote(referUrl)) 

                # Get the URL Path
                m = re.compile ("channel='(.*?)',").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("Last parse error")

                # Parse the final URL
                u = "plugin://plugin.video.colombiatv/?mode=publisher&host=janjua&channelid=" + streamPath
                print ("Final URL: " + u)
                return u
            except:
                pass
        