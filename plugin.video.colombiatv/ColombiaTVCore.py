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
from pyaes import openssl_aes
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
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        urllib2.install_opener(sys.modules["__main__"].opener)

        # SSL context since Kodi Krypton version
        try:
           import ssl
           ssl._create_default_https_context = ssl._create_unverified_context
        except:
           pass
        
        CHANNEL_URL = base64.b64decode("L3MvbjUxd2JudWNwYmZrZHkzL2NoYW5uZWxzLmpzb24/ZGw9MQ==") 
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
        
    #
    # Return the Show List 
    #
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
    # Return the stations list 
    #
    def getStationList(self, show):
        show_url = "https://" + DROPBOX_BASE_URL + base64.b64decode(urllib.unquote(show))
        request = urllib2.Request(show_url)
        requesturl = urllib2.urlopen(request)

        result = simplejson.load(requesturl)
        requesturl.close()

        if self.enabledebug == True:
            print (result['ColombiaRadio'])
        return result['ColombiaRadio']

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
            html = self.getRequestP2pcast("http://nowlive.club/stream.php?id=" + videoContentId + "&width=680&height=380&stretching=uniform&p=1", urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('curl = "(.*?)"').search(html)
            decodedURL = base64.b64decode(m.group(1))
            print ("decodedURL: " + decodedURL)
                        
            # Get the token
            html = self.getRequestP2pcast("http://nowlive.club/getToken.php", "http://nowlive.pw/stream.php?id=" + videoContentId, USER_AGENT, "XMLHttpRequest")
            m = re.compile('"token":"(.*?)"').search(html)
            token = m.group(1)
            print ("token: " + token)

            # Parse the final URL
            u = decodedURL + token + "|Referer=http://nowlive.club/stream.php?id=" + videoContentId + "&width=680&height=380&stretching=uniform&p=1&User-Agent=" + USER_AGENT
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
            html = self.getRequestP2pcast("http://widestream.io/embed-" + videoContentId, urllib.unquote(referUrl), USER_AGENT)
            m = re.compile('(http[^"]+\.m3u8[^"]*)').search(html)

            # Parse the final URL
            u = m.group(1) + '|Referer=' + referUrl + '&User-Agent=' + USER_AGENT + '&X-Requested-With=ShockwaveFlash/22.0.0.209&Host=cdn.widestream.io:8081'
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
        elif host == "247bay":
            STREAM_IP = "http://www.publish247.xyz:1935/loadbalancer"
            CHANNEL_URL = "http://www.247bay.tv/membedplayer/" + videoContentId + "/2/750/420"
            REFERER = "http://www.247bay.tv"
        elif host == "zenplayer":
            STREAM_IP = "http://www.zenexpublisher.com:1935/loadbalancer?25517&"
            CHANNEL_URL = "http://www.zenexplayer.com/membedplayer/" + videoContentId + "/1/740/415"
            REFERER = "http://www.zenexplayer.com"

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
    def getLw (self, videoContentId, sslPassword):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3171.0 Safari/537.36"

        try:
            # Get the stream IP Address http://embed.latino-webtv.com/win.html
        
            print ("VideoContent id: " + videoContentId)
            referURL = "http://embed.latino-webtv.com/channels/" + videoContentId + ".html"
            html = self.getRequestP2pcast(referURL, "http://embed.latino-webtv.com/", USER_AGENT)

            # Find the token get the cryptArr
            m = re.compile('= "(.*?)"').search(html)
            html = self.getRequestP2pcast("http://tvcanales.cf/" + m.group(1), "http://embed.latino-webtv.com/", USER_AGENT)
            m = re.compile('MarioCSdecrypt.dec\("(.*?)"\)').search(html)
            cryptArr = m.group(1)
            print cryptArr
            
            # Find the key
            html = self.getRequestP2pcast("http://js.latino-webtv.com/jquery-latest.js", "http://embed.latino-webtv.com/", USER_AGENT)
            opensslkey = sslPassword
            print "opensslkey = " + opensslkey

            OpenSSL_AES = openssl_aes.AESCipher()
            streamUrl = OpenSSL_AES.decrypt(cryptArr, opensslkey)
                   
            # Parse the final URL
            u = streamUrl + "|Referer=" + urllib.quote(referURL, safe='') + "&User-Agent=" + USER_AGENT + "&X-Requested-With=ShockwaveFlash/25.0.0.119"
            print ("Final URL: " + u)
            return u
        except Exception, e:
            print str(e)
            pass

    #
    # RCN HD App support
    #
    def getRCNApp (self):
        USER_AGENT = "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_2_1 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8C148 Safari/6533.18.5"

        try:
            # Get the token
            html = self.getRequestP2pcast("http://app.canalrcn.tech/js/indexAndroid5mas.js", "http://app.canalrcn.tech", USER_AGENT)
            m = re.compile("wifi.*stream\/(.*)\?autoplay").search(html)
            token = m.group(1)
            streamUrl = "http://mdstrm.com/live-stream-playlist/" + token + ".m3u8?&dnt=true&ref=http%3A%2F%2Fapp.canalrcn.tech%2Fandroid5mas%2Fwifi"
                                                
            # Parse the final URL
            u = streamUrl
            print ("Final URL: " + u)
            return u
        except:
            pass

    #
    # pxstream.tv support
    #
    def getPxstream (self, referUrl, videoContentId):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3046.0 Safari/537.36"

        try:
            # Get the stream IP Address
            print ("URL: " + referUrl + " --> " + urllib.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)
            html = self.getRequestP2pcast("http://pxstream.tv/embedrouter.php?file=" + videoContentId + "&width=680&height=380&jwplayer=flash", urllib.unquote(referUrl), USER_AGENT)

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
            html = self.getRequestP2pcast(base64.b64decode(urllib.unquote(referUrl)), "", USER_AGENT) 
            
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
                html = self.getRequestP2pcast(urllib.unquote(requestUrl), "", USER_AGENT) 

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
                html = self.getRequestP2pcast(urllib.unquote(requestUrl), "", USER_AGENT) 

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
                html = self.getRequestP2pcast(urllib.unquote(requestUrl), "", USER_AGENT) 

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
                html = self.getRequestP2pcast(urllib.unquote(requestUrl), urllib.unquote(refererUrl), USER_AGENT) 
                
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
        html = self.getRequestP2pcast(channelUrl, urllib.unquote(referUrl), USER_AGENT) 

        # Get the URL
        m = re.compile ('trap = "(.*?)"').search(html)
        streamPath = base64.b64decode(m.group(1))

        # Get the token
        html = self.getRequestP2pcast("http://bro.adca.st/nws.php", channelUrl, USER_AGENT, "XMLHttpRequest") 
        m = re.compile ('"rumba":"(.*?)"').search(html)
        token = m.group(1)

        # Parse the final URL
        u = streamPath + token + '|Referer=' + urllib.quote(channelUrl, safe='') + '&User-Agent=' + USER_AGENT
        print ("Final URL: " + u)
        return u
        
    #
    # cv support support
    #
    def getCVHLS (self, url):
        # Create the listitem
        u = base64.b64decode(urllib.unquote(url))
        print "u: " + u
        list_item = self.xbmcgui.ListItem(path=u)
        list_item.setProperty('inputstream.adaptive.manifest_type', 'hls')
        list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        list_item.setProperty('inputstream.adaptive.license_key', 'http://latinowebtv.ml/hls/key.php?token=U2FsdGVkX19QV9t4YnrB83%2F6MlMRunEqwS6VSfbQzeT5CmRRsEVlhXGS6D5E60wVxYqOFRaoj8Maxw64g84PTyuHE3O4QGfgU3hoVT1M9ntrhG4GO%2FQLVstUF6NhGaed')
        
        return list_item

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
        html = self.getRequestP2pcast(channelUrl, urllib.unquote(referUrl), USER_AGENT) 

        # Get the URL
        m = re.compile ('file: "(h.*?)"').search(html)
        streamPath = m.group(1)

        # Parse the final URL
        u = streamPath + '|Referer=' + urllib.quote(channelUrl, safe='') + '&User-Agent=' + USER_AGENT
        print ("Final URL: " + u)
        return u

    #
    # MPD hide support
    #
    def getCVMPD (self, url, url_webapi):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0"

        # Get the device_id and token
        response = urllib2.urlopen(base64.b64decode(urllib.unquote(url_webapi)))
        data = json.load(response)
        device_id = data['entry']['device_id']
        token = json.loads(data['response']['media']['challenge'])['token']
        print "device_id: " + device_id
        print "token: " + token

        # Get the certificate
        server_certificate = self.getRequestP2pcast("https://widevine-vod.clarovideo.net/licenser/getcertificate", "https://www.clarovideo.com", USER_AGENT)
        

        # Create the listitem
        list_item = self.xbmcgui.ListItem(path=url)
        list_item.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
        list_item.setProperty('inputstream.adaptive.license_key', 'https://widevine-vod.clarovideo.net/licenser/getlicense|Content-Type=|{"token":"' + token + '","device_id":"' + device_id + '","widevineBody":"b{SSM}"}|')
        list_item.setProperty('inputstream.adaptive.server_certificate', server_certificate);
        list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        list_item.setProperty('inputstreamaddon', 'inputstream.adaptive')
        list_item.setMimeType('application/dash+xml')
        list_item.setContentLookup(False)

        return list_item

    #
    # Vergol.com support
    # curl 'http://vergol.com/live3/winsports.php' -H 'Connection: keep-alive' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' -H 'Upgrade-Insecure-Requests: 1' -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3350.0 Safari/537.36' -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8' -H 'Referer: http://vercanalestv.com/tv/colombia/win-sports.html' 
    #
    