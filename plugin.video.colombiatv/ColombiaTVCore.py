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
# *  based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# */

import sys
import os

import simplejson
import urllib3
import cookielib
import subprocess
import re
import cgi
import gzip
import json
import base64
from StringIO import StringIO
from pyaes import openssl_aes
import jsUnwiser
import jsUnpack
import hqqresolver
import ssl
import xbmc

import ConfigParser
import xml.dom.minidom as minidom
from BeautifulSoup import BeautifulSoup

# ERRORCODES:
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

# Base URL for all querys. 
DROPBOX_BASE_URL='www.dropbox.com'
GITHUB_BASE_URL='gist.githubusercontent.com'

class ColombiaTVCore():
    #
    # Define the global variables for ColombiaTV
    #
    def __init__(self, instanceId=10, platformId=4, version=10):
        self.settings = sys.modules["__main__"].settings
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        self.enabledeveloper = sys.modules["__main__"].enabledeveloper
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        urllib2.install_opener(sys.modules["__main__"].opener)

        # SSL context since Kodi Krypton version
        try:
           import ssl
           ssl._create_default_https_context = ssl._create_unverified_context
        except:
           pass
        
        print "Developer Mode: " + self.settings.getSetting("enabledeveloper")
        if self.settings.getSetting("enabledeveloper") == "false":
            CHANNEL_URL = base64.b64decode("L3MvbjUxd2JudWNwYmZrZHkzL2NoYW5uZWxzLmpzb24/ZGw9MQ==") 
        else:
            CHANNEL_URL = base64.b64decode("L3MvYjhoanR3cHlpNml4YW9mL2NoYW5uZWxzZGV2Lmpzb24/ZGw9MQ==") #REALDEV
            
        self.url = "https://" + DROPBOX_BASE_URL + CHANNEL_URL
        
        CHANNEL_URL_BACKUP = base64.b64decode("L2RpZWdvZm4vYjAwMzYyMjc4YjFjYTE3MWIyN2ViNDBiZDdjMmQ1ZTQvcmF3Lw==")
        self.urlbackup = "https://" + GITHUB_BASE_URL + CHANNEL_URL_BACKUP + "channels.json"

    #
    # Return the URL from TV Channel
    #
    def getChannelList(self):
        try:
            request = urllib2.Request(self.url)
            requesturl = urllib2.urlopen(request)
            
            result = simplejson.load(requesturl)
            requesturl.close()
        
            if self.enabledeveloper == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']

        except:
            request = urllib2.Request(self.urlbackup)
            requesturl = urllib2.urlopen(request)

            result = simplejson.load(requesturl)
            requesturl.close()

            if self.enabledeveloper == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']
        
        
    #
    # Return the Show List 
    #
    def getShowList(self, show):
        show_url = "https://" + DROPBOX_BASE_URL + base64.b64decode(urllib.unquote(show))
        request = urllib2.Request(show_url)
        requesturl = urllib2.urlopen(request)

        result = simplejson.load(requesturl)
        requesturl.close()

        if self.enabledeveloper == True:
            print (result['ColombiaPlay'])
        return result['ColombiaPlay']

    #
    # Return the stations list 
    #
    def getStationList(self, show):
        show_url = "https://" + DROPBOX_BASE_URL + base64.b64decode(urllib.unquote(show))
        request = urllib2.Request(show_url)
        requesturl = urllib2.urlopen(request)

        result = simplejson.load(requesturl)
        requesturl.close()

        if self.enabledeveloper == True:
            print (result['ColombiaRadio'])
        return result['ColombiaRadio']

    #
    # URL Request
    #    
    def getRequest (self, url, referUrl, userAgent, xRequestedWith=""):
        UTF8 = 'utf-8'
        headers = {'User-Agent':userAgent, 'Referer':referUrl, 'X-Requested-With': xRequestedWith, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8'} 
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
    # URL Request
    #    
    def getRequestAdv (self, url, headers, isReplace=True):
        UTF8 = 'utf-8'
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
            
        if (isReplace):
            link1 = str(link1).replace('\n','')

        return(link1)

    #
    # Brightcove support
    #
    def demunge(self, munge):
        try:
            munge = urllib.unquote_plus(munge).decode(UTF8)
        except:
            pass
        return munge

    def getBrightcove (self, videoContentId, referUrl):
        print ("VideoContent id: " + videoContentId)

        USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/53.0.2785.86 Mobile/13G34 Safari/601.1.46"
        url = "http://c.brightcove.com/services/viewer/htmlFederated?&width=640&height=360&flashID=myExperience4042799614001&identifierClassName=BrightcoveExperienceID_9889&bgcolor=%23FFFFFF&wmode=transparent&playerID=4109933993001&playerKey=AQ~~%2CAAADexCiPmk~%2Chd5maXWwxzDmaeRpSVEvmO9M4jcJ6Ow3&isVid=true&isUI=true&dynamicStreaming=true&%40videoPlayer=" + videoContentId + "&includeAPI=true&templateLoadHandler=BCL.onTemplateLoad&templateReadyHandler=BCL.onTemplateReady&autoStart=&debuggerID=&startTime=1474130689252&refURL=not%20available"
        html = self.getRequest(url, referUrl, USER_AGENT)
        
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
            html = self.getRequest("http://p2pcast.tech/stream.php?id=" + videoContentId, "http://p2pcast.tech/stream.php?id=" + videoContentId + "&osr=0&p2p=0&stretching=uniform", USER_AGENT)
            m = re.compile('murl = "(.*?)"').search(html)
            decodedURL = base64.b64decode(m.group(1))
            print ("decodedURL: " + decodedURL)
                        
            # Get the token
            html = self.getRequest("http://p2pcast.tech/getTok.php", "http://p2pcast.tech/stream.php?id=" + videoContentId, USER_AGENT, "XMLHttpRequest")
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
            html = self.getRequest("http://nowlive.pro/1/" + videoContentId + ".html?id=" + videoContentId + videoContentId, urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('application\/x-mpegurl.*\/\/(.*?)m3u8').search(html)
            decodedURL = m.group(1)
            print ("decodedURL: " + decodedURL)
                        
            # Parse the final URL
            u = "http://" + decodedURL + "m3u8" + "|Referer=" + urllib.unquote(referUrl) + "&User-Agent=" + USER_AGENT
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # Widestream support
    #
    def getWideStream (self, referUrl, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the decodeURL
            print ("VideoContent id: " + videoContentId)
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            html = self.getRequest("http://widestream.io/embed-" + videoContentId, urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('(http[^"]+\.m3u8[^"]*)').search(html)

            # Parse the final URL
            u = m.group(1) + '|Referer=' + referUrl + '&User-Agent=' + USER_AGENT + '&Host=ultra.widestream.io:8081'
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
            html = self.getRequest("http://www.caston.tv/player.php?id=" + videoContentId, "http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390", USER_AGENT)
            m = re.compile('unescape\(\'(.*)\'\)\);').search(html)
            unWiser = jsUnwiser.JsUnwiser()
            unWiserContent = unWiser.unwiseAll(urllib.unquote(m.group(1)))
                        
            # Get the decodedURL
            m = re.compile('file:"(.*?)"').search(unWiserContent)
            decodedURL = m.group(1)
            print ("decodedURL: " + decodedURL)

            # Get the token
            html = self.getRequest("http://www.caston.tv/sssss.php", "http://www.caston.tv/player.php?id=" + videoContentId + "&width=680&height=390", USER_AGENT, "XMLHttpRequest")
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
            STREAM_IP = "https://mstable.pw/loadbalancer?273018"
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
            CHANNEL_URL = "http://www.janjuaplayer.com/sharedcdn/membedplayer/" + videoContentId + "/1/680/380"
            REFERER = "http://www.janjuaplayer.com"
        elif host == "zony":
            STREAM_IP = "http://cdn.pubzony.com:1935/loadbalancer"
            CHANNEL_URL = "http://www.zony.tv/membedplayer/" + videoContentId + "/1/620/380"
            REFERER = "http://www.zony.tv"
        elif host == "247bay":
            STREAM_IP = "http://www.publish247.xyz:1935/loadbalancer"
            CHANNEL_URL = "http://www.247bay.tv/membedplayer/" + videoContentId + "/2/750/420"
            REFERER = "http://www.247bay.tv"
        elif host == "zenplayer":
            STREAM_IP = "http://www.zenexpublisher.com:1935/loadbalancer?25517&"
            CHANNEL_URL = "http://www.zenexplayer.com/membedplayer/" + videoContentId + "/1/740/415"
            REFERER = "http://www.zenexplayer.com"
        elif host == "playerfs":
            STREAM_IP = "http://www.pubfstream.com:1935/loadbalancer"
            CHANNEL_URL = "http://www.playerfs.com/hembedplayer/" + videoContentId + "/2/650/400"
            REFERER = "http://www.playerfs.com"
        elif host == "playuc":
            STREAM_IP = "https://www.lquest123b.top/loadbalancer?109348"
            CHANNEL_URL = "https://www.playuc.live/membedplayer/" + videoContentId + "/1/640/360"
            REFERER = "https://cdn.chatytvgratis.net"

        try:
            # Get the stream IP Address
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest(STREAM_IP, REFERER, USER_AGENT)
            m = re.compile('redirect=(.*)').search(html)
            ipAddress = m.group(1)
            print ("ipAddress: " + ipAddress)
                                    
            # Get the m3u8 URL
            html = self.getRequest(CHANNEL_URL, REFERER, USER_AGENT)
            m = re.compile('ea \+ \"(.*?)\"').search(html)
            m3u8Address = m.group(1)
            print ("m3u8Address: " + m3u8Address)

            # Get the private key
            if host == "mips" or host == "playuc": 
                m = re.compile('enableVideo\(\"(.*?)\"').search(html)
                pk = m.group(1)
                pk = pk[:2] + pk[3:]

                m3u8Address = m3u8Address + pk
                print ("m3u8Address final: " + m3u8Address)
                
            # Parse the final URL
            u = "https://" + ipAddress + m3u8Address
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # lw.ml support
    #
    def getLw (self, videoContentId):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3171.0 Safari/537.36"

        try:
            # Get the stream IP Address http://tv.jaffmisshwedd.com/channels/win.html
        
            print ("VideoContent id: " + videoContentId)
            referURL = "http://tv.jaffmisshwedd.com/channels/" + videoContentId + ".html"
            html = self.getRequest(referURL, "http://embed.latino-webtv.com/", USER_AGENT)

            # Find the cryptArr
            m = re.compile('MarioCSdecrypt.dec\("(.*?)"\)').search(html)
            cryptArr = m.group(1)
            print cryptArr
            
            # Find the key
            headers = {'User-Agent':USER_AGENT, 'Referer':referURL, 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
            html = self.getRequestAdv("http://tv.jaffmisshwedd.com/config-player.js", headers)

            m = re.compile("'decode','slice','(\w+?)'\]").search(html)
            opensslkey = m.group(1)
            print "opensslkey = " + opensslkey

            OpenSSL_AES = openssl_aes.AESCipher()
            streamUrl = OpenSSL_AES.decrypt(cryptArr, opensslkey)

            # Get the balancer server
            headers = {'User-Agent':USER_AGENT, 'Referer':referURL, 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
            balancer = self.getRequestAdv("http://mariocs.com:2082/loadbalance", headers)
            
            # Parse the final URL
            u = balancer + streamUrl + "|Referer=" + urllib.quote(referURL, safe='') + "&User-Agent=" + USER_AGENT + "&X-Requested-With=ShockwaveFlash/25.0.0.119"
            print ("Final URL: " + u)
            return u
        except Exception, e:
            print str(e)
            pass

    #
    # RCN HD App support
    # http://app.canalrcn.tech/js/indexAndroid5mas.js http://app.canalrcn.tech
    #
    
    #
    # limpi.tv support
    #
    def getLimpitv (self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3046.0 Safari/537.36"

        try:
            # Get the first stream IP Address
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest("https://player.limpi.tv/embed.js", urllib.unquote(referUrl), USER_AGENT)

            # Get the second stream IP address
            m = re.compile("src=\"(.*?)\'").search(html)
            secondReferUrl = m.group(1)
            html = self.getRequest(secondReferUrl + videoContentId, urllib.unquote(referUrl), USER_AGENT)
            m = re.compile("source: \"(.*?)\"").search(html)
            streamUrl = m.group(1)
                                                            
            # Parse the final URL
            u = streamUrl + "|Referer=" + urllib.quote(secondReferUrl + videoContentId, safe='') + "&User-Agent=" + USER_AGENT 
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # Pxstream.tv support
    #
    def getPxstream (self, referUrl, videoContentId):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3046.0 Safari/537.36"

        try:
            # Get the stream IP Address
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest("http://pxstream.tv/embedrouter.php?file=" + videoContentId + "&width=680&height=380&jwplayer=flash", urllib.unquote(referUrl), USER_AGENT)

            # Find and decode the URL
            m = re.compile("source: '(.*?)'").search(html)
            streamUrl = m.group(1)
            print ("streamUrl: " + streamUrl)
                                    
            # Parse the final URL
            u = streamUrl + "|Referer=" + urllib.quote("http://pxstream.tv/embedrouter.php?file=" + videoContentId + "&width=680&height=380&jwplayer=seven", safe='') + "&User-Agent=" + USER_AGENT 
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
            html = self.getRequest(base64.b64decode(urllib.unquote(referUrl)), "", USER_AGENT) 
            
            # Get the URL Path
            m = re.compile ("([^:]*)canal=" + channelId + "(.*?)<\/link>").search(html)
            if m:
                streamPath = "http:" + m.group(1) + "canal=" + channelId + m.group(2)
                streamPath = streamPath.replace('&amp;', '&')
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
    def getRandom (self, host, requestUrl, refererUrl=""):
        if host == "ssh101":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
                print ("URL: " + requestUrl + " --> " + urllib.unquote(requestUrl))
                html = self.getRequest(urllib.unquote(requestUrl), "", USER_AGENT) 

                # Get the URL Path
                m = re.compile ("'file': '(.*?)',").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("parse error")

                # Parse the final URL
                u = streamPath
                print ("Final URL: " + u)
                return u
            except:
                pass

        elif host == "janjua":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
                print ("URL: " + requestUrl + " --> " + urllib.unquote(requestUrl))
                html = self.getRequest(urllib.unquote(requestUrl), "", USER_AGENT) 

                # Get the URL Path
                m = re.compile ("channel='(.*?)',").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("parse error")

                # Parse the final URL
                u = "plugin://plugin.video.colombiatv/?mode=publisher&host=janjua&channelid=" + streamPath
                print ("Final URL: " + u)
                return u
            except:
                pass

        elif host == "vk":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
                print ("URL: " + requestUrl + " --> " + urllib.unquote(requestUrl))
                html = self.getRequest(urllib.unquote(requestUrl), "", USER_AGENT) 

                # Get the URL Path
                m = re.compile ('file:\s+"(.*?)"').search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("parse error")

                # Parse the final URL
                u = streamPath
                print ("Final URL: " + u)
                return u
            except:
                pass

        elif host == "vergol":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0"
                print ("URL: " + requestUrl + " --> " + urllib.unquote(requestUrl))
                print ("Referer URL: " + refererUrl + " --> " + urllib.unquote(refererUrl))
                html = self.getRequest(urllib.unquote(requestUrl), urllib.unquote(refererUrl), USER_AGENT) 
                
                # Get the URL Path
                m = re.compile ("source:\s+'(.*?)'").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("parse error")

                # Parse the final URL
                u = streamPath + "|Referer=" + urllib.unquote(requestUrl) + "&User-Agent=" + USER_AGENT
                print ("Final URL: " + u)
                return u
            except:
                pass
        
    #
    # Bro.adca.st support
    #
    def getBroadcastSite (self, channelId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
        channelUrl = "http://bro.adca.st/stream.php?id=" + channelId + "&p=1&c=0&stretching=uniform&old=0"
        html = self.getRequest(channelUrl, urllib.unquote(referUrl), USER_AGENT) 

        # Get the URL
        m = re.compile ('tambor = "(.*?)"').search(html)
        streamPath = m.group(1)
        
        # Get the tokenpage
        m = re.compile ('firme = "(.*?)"').search(html)
        tokenpage = m.group(1)
        
        # Get the token
        html = self.getRequest("http://bro.adca.st/" + tokenpage, channelUrl, USER_AGENT, "XMLHttpRequest") 
        m = re.compile (':"(.*?)"').search(html)
        token = m.group(1)

        # Parse the final URL
        u = streamPath + token + '|Referer=' + urllib.quote(channelUrl, safe='') + '&User-Agent=' + USER_AGENT + "&Origin=http://bro.adca.st"
        print ("Final URL: " + u)
        return u
        
    #
    # Radiotime.com support
    #
    def getRadiotime (self, station):
        streamPath = "http://opml.radiotime.com/Tune.ashx?formats=aac,html,mp3,ogg,qt,real,flash,wma,wmpro,wmvideo,wmvoice&partnerId=RadioTime&id=" + station
        streams = []

        # Get the streamlist
        request = urllib2.Request(streamPath)
        file = urllib2.urlopen(request)
        for line in file:
            print('StreamURL: %s' % line)

            # PLS file
            m = re.compile ("\.pls").search(line)
            if m:
                requestPls = urllib2.Request(line)
                filePls = urllib2.urlopen(requestPls)
                for linePls in filePls:
                    mPls = re.compile ("File.*?=(.*)").search(linePls)
                    if mPls:
                        streams.append(mPls.group(1))
                     
                filePls.close()

            # M3U or playlist file
            elif len(line.strip()) > 0 and not line.strip().startswith('#'):
                streams.append(line.strip())
        
        file.close()

        # Parse the final URL
        if (streams):
            u = streams[0]
            print ("Final URL: " + u)
            return u

    #
    # gamovideo.com support
    #
    def getGamovideo (self, vid):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
        referUrl = "http://gamovideo.com"
        channelUrl = "http://gamovideo.com/embed-" + vid + "-600x400.html"
        html = self.getRequest(channelUrl, urllib.unquote(referUrl), USER_AGENT) 

        # Get the URL
        m = re.compile ('file: "(h.*?)"').search(html)
        streamPath = m.group(1)

        # Parse the final URL
        u = streamPath + '|Referer=' + urllib.quote(channelUrl, safe='') + '&User-Agent=' + USER_AGENT
        print ("Final URL: " + u)
        return u

    #
    # HLS CV support
    #
    def getCVHLS (self, url):
        USER_AGENT = "AppleCoreMedia/1.0.0.15E302 (iPhone; U; CPU OS 11_3_1 like Mac OS X; en_us)"
        headers = {'User-Agent':USER_AGENT, 
                    'Referer': 'https://www.clarovideo.com', 
                    'Pragma': 'akamai-x-get-client-ip, akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-check-cacheable, akamai-x-get-cache-key, akamai-x-get-extracted-values, akamai-x-get-nonces, akamai-x-get-ssl-client-session-id, akamai-x-get-true-cache-key, akamai-x-serial-no, akamai-x-feo-trace, akamai-x-get-request-id' } 
        request = urllib2.Request (base64.b64decode(urllib.unquote(url)), None, headers)
        response = urllib2.urlopen(request)
        data = json.load(response)
        video_url = data['response']['media']['video_url']
        print "video_url: " + video_url

        # Parse the final URL
        stream = '{0}|User-Agent={1}'
        u = stream.format(video_url, USER_AGENT)
        return u
        
    #
    # MPD hide support
    #
    def getCVMPD (self, url, url_webapi):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3730.0 Safari/537.36"

        # Get the device_id and token
        headers = {'User-Agent': USER_AGENT, 'Referer': 'https://www.clarovideo.com' } 
        request = urllib2.Request (base64.b64decode(urllib.unquote(url_webapi)), None, headers)
        response = urllib2.urlopen(request)
        data = json.load(response)
        device_id = data['entry']['device_id']
        token = json.loads(data['response']['media']['challenge'])['token']
        print "device_id: " + device_id
        print "token: " + token

        # Get the certificate
        server_certificate = self.getRequest("https://widevine-vod.clarovideo.net/licenser/getcertificate", "https://www.clarovideo.com", USER_AGENT)
        
        # Create the listitem
        list_item = self.xbmcgui.ListItem(path=url + '|Referer=' + urllib.unquote("https://www.clarovideo.com") + '&User-Agent=' + USER_AGENT)
        list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        list_item.setProperty('inputstream.adaptive.license_key', 'https://widevine-claroglobal-vod.clarovideo.net/licenser/getlicense|Content-Type=|{"token":"' + token + '","device_id":"' + device_id + '","widevineBody":"b{SSM}"}|')
        list_item.setProperty('inputstream.adaptive.server_certificate', server_certificate);
        list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        list_item.setMimeType('application/dash+xml')
        list_item.setContentLookup(False)

        return list_item

    #
    # Streamango support
    #
    def getStreamango (self, vid):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
        referUrl = "ffsamqtncpfdpbrd"
        channelUrl = "https://streamango.com/f/" + vid
        html = self.getRequest(channelUrl, "", USER_AGENT) 

        # Get the URL
        m = re.compile ("type:\"video\/([^\"]+)\",src:d\('([^']+)',(.*?)\).+?height:(\d+)").search(html)

        if (m.group (1)):
            ext = m.group(1)
            encoded = m.group(2)
            code = m.group(3)
            quality = m.group(4)

            # Get the URL
            unWiser = jsUnwiser.JsUnwiser()
            streamPath = unWiser.decode(encoded, int(code))
            streamPath = streamPath.replace("@","")
            if not streamPath.startswith("http"):
                streamPath = "http:" + streamPath

            # Parse the final URL
            u = streamPath
            print ("Final URL: " + u)
            return u

    #
    # Okru support
    #
    def getOkru (self, vid):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
        channelUrl = "https://ok.ru/video/" + vid
        html = self.getRequest(channelUrl, "", USER_AGENT) 

        #
        # Unscape HTML
        #
        html = BeautifulSoup(html, convertEntities=BeautifulSoup.HTML_ENTITIES)
        unscapeHtml = str(html).replace("\\", "")

        # Get the URL
        m = re.findall (r'\{"name":"([^"]+)","url":"([^"]+)"', unscapeHtml)
        if m:
            for m_element in m:
                if m_element[0] == "sd": #hd
                    u = m_element[1].replace("%3B", ";").replace("u0026", "&")
                elif m_element[0] == "low": 
                    u = m_element[1].replace("%3B", ";").replace("u0026", "&")
                
        print ("Final URL: " + u)
        return u

    #
    # kastream.biz support
    #
    def getKastream (self, videoContentId, referUrl):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the decodeURL
            print ("VideoContent id: " + videoContentId)
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            html = self.getRequest("http://kastream.biz/embed.php?file=" + videoContentId, urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('source.*?:.*?"(.*?)"').search(html)

            # Parse the final URL
            u = "http:" + m.group(1) + '|Referer=' + referUrl + '&User-Agent=' + USER_AGENT
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # whostreams.net support
    #
    def getWhostreams (self, videoContentId, referUrl):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3448.0 Safari/537.36"

        # Get the decodeURL
        print ("VideoContent id: " + videoContentId)
        print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
        html = self.getRequestAdv("https://whostreams.net/embed/" + videoContentId, headers, False)
        
        #
        # Unpack URL
        #
        wsParams = re.compile('<script>(e.*)').search(html)
        if (wsParams):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(wsParams.group(1))
            print (unPack)
            
            #
            # Find URL
            #
            wsUrl = re.compile('src:"(.*?)"').search(unPack)
            if (wsUrl):
                u = wsUrl.group(1) + '|Referer=' + urllib.unquote(referUrl) + '&User-Agent=' + USER_AGENT
                print ("Final URL: " + u)
                return u 

    #
    # tl.tv support
    #
    def getTlTv (self, channelId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.5 Safari/537.36"
        channelUrl = base64.b64decode("aHR0cHM6Ly90ZWxlcml1bS50di9lbWJlZC8=") + channelId + ".html"
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
        html = self.getRequestAdv(channelUrl, headers, False) 

        dataUnpack = re.compile('(eval\(function\(p,a,c,k,e,d\).*)').search(html)
        if (dataUnpack):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(dataUnpack.group(1))
            if self.enabledebug: print "unPack: " + unPack

            # Get the Token URL 
            varNames = re.compile('\{url:.*?atob\((\w*?)\).*?\+.*?atob\((\w*?)\),dataType\s*:\s*[\'\"]json[\'\"]')
            
            vars = varNames.findall(unPack)[0]
            part1Reversed = re.compile('{0}\s*=\s*[\'\"](.+?)[\'\"];'.format(vars[0])).findall(unPack)[0]
            part2Reversed = re.compile('{0}\s*=\s*[\'\"](.+?)[\'\"];'.format(vars[1])).findall(unPack)[0]
            part1 = base64.b64decode(part1Reversed)[8:]
            part2 = base64.b64decode(part2Reversed)
            if self.enabledebug: print "part1 + part2: " + part1 + part2

            # Get the real token
            tokenUrl = base64.b64decode('aHR0cHM6Ly90ZWxlcml1bS50dg==') + part1 + part2
            headers = { 'Accept':'application/json, text/javascript, */*; q=0.01', 
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language':'en-US,en;q=0.9,es-CO;q=0.8,es;q=0.7',
                        'Connection':'keep-alive',
                        'User-Agent':USER_AGENT, 
                        'Referer':channelUrl,  
                        'Sec-Fetch-Mode':'cors',  
                        'Sec-Fetch-Site':'same-origin',  
                        'X-Requested-With': 'XMLHttpRequest',
                        'Cookie': 'volumeVar=100; _ga=GA1.2.820523732.1566237251; ChorreameLaJa=100'} 
            tokenJson = self.getRequestAdv(tokenUrl, headers, False)
            if self.enabledebug: print "tokenJson: " + tokenJson
            simpleTokenJson = json.loads(tokenJson)

            if (simpleTokenJson):
                tokenHtml = simpleTokenJson[5][::-1]
                if self.enabledebug: print "tokenHtml " + tokenHtml

            # Get the real CDN Url
            varCdn = re.compile('if\(isXMobile\)\{(\w*?)=.*?\};')
            vars = varCdn.findall(unPack)
            cdnReversed = re.compile('{0}\s*=\s*[\'\"](.+?)[\'\"];'.format(vars[0])).findall(unPack)[0]
            cdn = base64.b64decode(cdnReversed)
            if self.enabledebug: print "cdn: " + cdn

            # Parse the final URL
            stream = 'https:{0}{1}|Referer={2}&User-Agent={3}&Origin={4}&Connection=keep-alive&Accept=*/*'
            u = stream.format(cdn, tokenHtml, urllib.quote(channelUrl, safe=''), USER_AGENT, base64.b64decode('aHR0cHM6Ly90ZWxlcml1bS50dg=='))
            return u

    #
    # wstream.to support
    #
    def getWstream(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3730.0 Safari/537.36"
        channelUrl = "https://wstream.to/embed/" + videoContentId
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
        html = self.getRequestAdv(channelUrl, headers, False) 

        dataUnpack = re.compile('(eval\(function\(p,a,c,k,e,d\).*)').search(html)
        if (dataUnpack):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(dataUnpack.group(1))

            # Get the URL
            m = re.compile('src:"(.+?)"').search(unPack)
            streamUrl = ""
            if (m):
                streamUrl = m.group(1)

            # Parse the final URL
            stream = '{0}|Referer={1}&User-Agent={2}'
            u = stream.format(streamUrl, urllib.quote(channelUrl, safe=''), USER_AGENT)
            return u


    #
    # premiumtvchannels.tv support
    #
    def getPremiumtv(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3730.0 Safari/537.36"
        channelUrl = "http://premiumtvchannels.com/clappr/" + videoContentId + ".php"
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
        html = self.getRequestAdv(channelUrl, headers, False) 
        print "html" + html 

        m = re.compile('file: "(.*?)"').search(html)
        if (not m):
            m = re.compile('source: "(.*?)"').search(html)

        if (m):
            streamUrl = m.group(1)
            
            # Parse the final URL
            stream = '{0}|Referer={1}&User-Agent={2}'
            u = stream.format(streamUrl, urllib.quote(channelUrl, safe=''), USER_AGENT)
            return u
    
    