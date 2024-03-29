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

import simplejson
import urllib3
import certifi
import urllib.parse
import subprocess
import re
import cgi
import gzip
import json
import base64
import io
from datetime import datetime, timedelta

import jsUnwiser
import jsUnpack
import hqqresolver
import xbmc

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from pyaes import openssl_aes
from bs4 import BeautifulSoup

# ERRORCODES:
# 200 = OK
# 303 = See other (returned an error message)
# 500 = uncaught error

# Base URL for all querys. 
DROPBOX_BASE_URL = "www.dropbox.com"
GITHUB_BASE_URL = "gist.githubusercontent.com"

class ColombiaTVCore():
    #
    # Define the global variables for ColombiaTV
    #
    def __init__(self, instanceId=10, platformId=4, version=10):
        self.addon = sys.modules["__main__"].addon
        self.plugin = sys.modules["__main__"].plugin
        self.enabledebug = sys.modules["__main__"].enabledebug
        self.enabledeveloper = sys.modules["__main__"].enabledeveloper
        self.xbmcgui = sys.modules["__main__"].xbmcgui
        
        # SSL context since Kodi Krypton version
        try:
           import ssl
           ssl._create_default_https_context = ssl._create_unverified_context
        except:
           pass
        
        print ("Developer Mode: " + self.addon.getSetting("enabledeveloper"))
        if self.addon.getSetting("enabledeveloper") == "false":
            CHANNEL_URL = base64.b64decode("L3MvbjUxd2JudWNwYmZrZHkzL2NoYW5uZWxzLmpzb24/ZGw9MQ==").decode('utf-8')
        else:
            CHANNEL_URL = base64.b64decode("L3MvYjhoanR3cHlpNml4YW9mL2NoYW5uZWxzZGV2Lmpzb24/ZGw9MQ==").decode('utf-8') #REALDEV
            
        self.url = "https://{0}{1}".format(DROPBOX_BASE_URL, CHANNEL_URL)
        
        CHANNEL_URL_BACKUP = base64.b64decode("L2RpZWdvZm4vYjAwMzYyMjc4YjFjYTE3MWIyN2ViNDBiZDdjMmQ1ZTQvcmF3Lw==").decode('utf-8')
        self.urlbackup = "https://{0}{1}channels.json".format(GITHUB_BASE_URL, CHANNEL_URL_BACKUP)

    #
    # Return the URL from TV Channel
    #
    def getChannelList(self):
        try:
            http = urllib3.PoolManager(ca_certs=certifi.where())

            response = http.request('GET', self.url)
            result = simplejson.loads(response.data.decode('utf-8'))
        
            if self.enabledeveloper == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']

        except:
            http = urllib3.PoolManager(ca_certs=certifi.where())

            response = http.request('GET', self.urlbackup)
            result = simplejson.load(response.data.decode('utf-8'))

            if self.enabledeveloper == True:
                print (result['ColombiaTV'])
            return result['ColombiaTV']
        
        
    #
    # Return the Show List 
    #
    def getShowList(self, show):
        show_url = "https://{0}{1}".format(DROPBOX_BASE_URL, base64.b64decode(urllib.parse.unquote(show)).decode('utf-8'))
        http = urllib3.PoolManager(ca_certs=certifi.where())

        response = http.request('GET', show_url)
        result = simplejson.loads(response.data.decode('utf-8'))

        if self.enabledeveloper == True:
            print (result['ColombiaPlay'])
        return result['ColombiaPlay']

    #
    # Return the stations list 
    #
    def getStationList(self, show):
        show_url = "https://{0}{1}".format(DROPBOX_BASE_URL, base64.b64decode(urllib.parse.unquote(show)).decode('utf-8'))
        http = urllib3.PoolManager(ca_certs=certifi.where())

        response = http.request('GET', show_url)
        result = simplejson.loads(response.data.decode('utf-8'))

        if self.enabledeveloper == True:
            print (result['ColombiaRadio'])
        return result['ColombiaRadio']

    #
    # URL Request
    # Python3 migrated
    #    
    def getRequest (self, url, referUrl, userAgent, xRequestedWith=""):
        headers = {'User-Agent':userAgent, 'Referer':referUrl, 'X-Requested-With': xRequestedWith, 'Accept':"text/html", 'Accept-Encoding':'gzip,deflate,sdch', 'Accept-Language':'en-US,en;q=0.8'} 
        
        try:
            http = urllib3.PoolManager(ca_certs=certifi.where())
            response = http.request('GET', url, headers)
            
            link1 = response.data.decode('utf-8')
        except:
            link1 = ""
        
        link1 = str(link1).replace('\n','')
        return(link1)

    #
    # URL Request
    # Python3 migrated
    #    
    def getRequestAdv (self, url, headers, isReplace=True):
        
        try:
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                        ca_certs=certifi.where(),
                                        retries=10)
            response = http.request('GET', url, headers)
            
            link1 = response.data.decode('utf-8')
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
            munge = urllib.parse.unquote_plus(munge).decode(UTF8)
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
    def getNowLive (self, referUrl, videoContentId):
        #
        # Global variables
        #
        USER_AGENT = "Mozilla/5.0 (X11 Linux i686 rv:41.0) Gecko/20100101 Firefox/41.0 Iceweasel/41.0.2"

        try:
            # Get the decodeURL
            print ("VideoContent id: " + videoContentId)
            print ("URL: " + referUrl + " --> " + urllib.parse.unquote(referUrl))
            html = self.getRequest("http://nowlive.pro/1/" + videoContentId + ".html?id=" + videoContentId + videoContentId, urllib.parse.unquote(referUrl), USER_AGENT)
            m = re.compile('application\/x-mpegurl.*\/\/(.*?)m3u8').search(html)
            decodedURL = m.group(1)
            print ("decodedURL: " + decodedURL)
                        
            # Parse the final URL
            u = "http://" + decodedURL + "m3u8" + "|Referer=" + urllib.parse.unquote(referUrl) + "&User-Agent=" + USER_AGENT
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
            print ("URL: " + referUrl + " --> " + urllib.parse.unquote(referUrl))
            print ("VideoContent id: " + videoContentId)
            html = self.getRequest("https://player.limpi.tv/embed.js", urllib.parse.unquote(referUrl), USER_AGENT)

            # Get the second stream IP address
            m = re.compile("src=\"(.*?)\'").search(html)
            secondReferUrl = m.group(1)
            html = self.getRequest(secondReferUrl + videoContentId, urllib.parse.unquote(referUrl), USER_AGENT)
            m = re.compile("source: \"(.*?)\"").search(html)
            streamUrl = m.group(1)
                                                            
            # Parse the final URL
            u = streamUrl + "|Referer=" + urllib.parse.quote(secondReferUrl + videoContentId, safe='') + "&User-Agent=" + USER_AGENT 
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
    # Random support
    #
    def getRandom (self, host, requestUrl, refererUrl=""):
        if host == "ssh101":
            USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4466.0 Safari/537.36"
            
            headers = {
                'authority': 'ssh101.com',
                'upgrade-insecure-requests': '1',
                'user-agent': USER_AGENT, 
                'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                'referer': urllib.parse.unquote(refererUrl),
                'accept-language': 'en-US,en;q=0.9,es-CO;q=0.8,es;q=0.7'
            } 
            channelUrl = base64.b64decode(urllib.parse.unquote(requestUrl)).decode('utf-8')
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            html = requests.get(channelUrl, headers=headers).text
            
            # Get the URL Path
            m = re.compile ("source src=\"(.*?)\"").search(html)
            if m:
                streamPath = m.group(1)
            else:
                print ("parse error")

            # Parse the final URL
            u = streamPath + "|Referer=" + urllib.parse.quote(channelUrl, safe='') + "&User-Agent=" + USER_AGENT 
            print ("Final URL: " + u)
            return u
            
        elif host == "janjua":
            try:
                USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
                print ("URL: " + requestUrl + " --> " + urllib.parse.unquote(requestUrl))
                html = self.getRequest(urllib.parse.unquote(requestUrl), "", USER_AGENT) 

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
                print ("URL: " + requestUrl + " --> " + urllib.parse.unquote(requestUrl))
                html = self.getRequest(urllib.parse.unquote(requestUrl), "", USER_AGENT) 

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
                print ("URL: " + requestUrl + " --> " + urllib.parse.unquote(requestUrl))
                print ("Referer URL: " + refererUrl + " --> " + urllib.parse.unquote(refererUrl))
                html = self.getRequest(urllib.parse.unquote(requestUrl), urllib.parse.unquote(refererUrl), USER_AGENT) 
                
                # Get the URL Path
                m = re.compile ("source:\s+'(.*?)'").search(html)
                if m:
                    streamPath = m.group(1)
                else:
                    print ("parse error")

                # Parse the final URL
                u = streamPath + "|Referer=" + urllib.parse.unquote(requestUrl) + "&User-Agent=" + USER_AGENT
                print ("Final URL: " + u)
                return u
            except:
                pass
        
    #
    # Radiotime.com support
    # Python3 migrated
    #
    def getRadiotime (self, station):
        streamPath = "http://opml.radiotime.com/Tune.ashx?formats=aac,html,mp3,ogg,qt,real,flash,wma,wmpro,wmvideo,wmvoice&partnerId=RadioTime&id=" + station
        streams = []

        # Get the streamlist
        http = urllib3.PoolManager(ca_certs=certifi.where())
        response = http.request('GET', streamPath)
                
        for line in response.data.decode('utf-8').splitlines():
            print('StreamURL: %s' % line)

            # PLS file
            m = re.compile ("\.pls").search(line)
            if m:
                requestPls = urllib3.Request(line)
                filePls = urllib3.urlopen(requestPls)
                for linePls in filePls:
                    mPls = re.compile ("File.*?=(.*)").search(linePls)
                    if mPls:
                        streams.append(mPls.group(1))
                     
                filePls.close()

            # M3U or playlist file
            elif len(line.strip()) > 0 and not line.strip().startswith('#'):
                streams.append(line.strip())
        
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
        html = self.getRequest(channelUrl, urllib.parse.unquote(referUrl), USER_AGENT) 

        # Get the URL
        m = re.compile ('file: "(h.*?)"').search(html)
        streamPath = m.group(1)

        # Parse the final URL
        u = streamPath + '|Referer=' + urllib.parse.quote(channelUrl, safe='') + '&User-Agent=' + USER_AGENT
        print ("Final URL: " + u)
        return u

    #
    # HLS CV support
    #
    def getCVHLS (self, url, user_token):
        USER_AGENT = "com.dla.ClaroVideo/1 CFNetwork/1197 Darwin/20.0.0"

        headers = {'User-Agent':USER_AGENT, 
                    'Referer': 'https://www.clarovideo.com', 
                    'Pragma': 'akamai-x-get-client-ip, akamai-x-cache-on, akamai-x-cache-remote-on, akamai-x-check-cacheable, akamai-x-get-cache-key, akamai-x-get-extracted-values, akamai-x-get-nonces, akamai-x-get-ssl-client-session-id, akamai-x-get-true-cache-key, akamai-x-serial-no, akamai-x-feo-trace, akamai-x-get-request-id' } 
        
        media_url = base64.b64decode(urllib.parse.unquote(url)).decode('utf-8')
        print ("media_url: " + media_url)

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        if (not user_token):
            html = requests.get(media_url, headers=headers).content
        else:
            data = {"payway_token": "", "user_token": user_token} 
            html = requests.post(media_url, headers=headers, data=data).content

        data = json.loads(html)
        video_url = data['response']['media']['video_url']
        print ("video_url: " + video_url)

        # Parse the final URL
        stream = '{0}|User-Agent={1}'
        u = stream.format(video_url, USER_AGENT)
        return u
        
    #
    # MPD hide support
    #
    def getCVMPD (self, url):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4680.2 Safari/537.36"

        # Get the device_id and token
        media_url = "https://mfwkweb-api.clarovideo.net/services/player/getmedia?api_version=v5.92&authpn=html5player&authpt=ad5565dfgsftr&format=json&region=colombia&device_id=beac6d8fdd97a5e184ace84f9988a0fc&device_category=web&device_model=html5&device_type=html5&device_so=Chrome&device_manufacturer=windows&HKS=(6af6dfd46e777a2ab797e40b007f9e75)&stream_type=dashwv&group_id=888842&preview=0&css=0&device_name=Chrome&crDomain=https://www.clarovideo.com"
        headers = {'User-Agent': USER_AGENT, 'Referer': 'https://www.clarovideo.com' } 

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.post(media_url, headers=headers).content
        data = json.loads(html)
        device_id = "beac6d8fdd97a5e184ace84f9988a0fc"
        token = json.loads(data['response']['media']['challenge'])['token']
        material_id = json.loads(data['response']['media']['challenge'])['material_id']
        print ("device_id: " + device_id)
        print ("token: " + token)
        print ("material_id: " + token)

        # Get the certificate
        server_certificate = self.getRequest("https://widevine-vod.clarovideo.net/licenser/getcertificate", "https://www.clarovideo.com", USER_AGENT)
        
        # Get the mpd URL 
        media_url = base64.b64decode(urllib.parse.unquote(url)).decode('utf-8')
        print ("media_url: " + media_url)

        # Create the listitem
        list_item = self.xbmcgui.ListItem(path=media_url + '|User-Agent=' + USER_AGENT)
        list_item.setProperty('inputstream.adaptive.license_type', 'com.microsoft.playready')
        #list_item.setProperty('inputstream.adaptive.license_key', 'https://widevine-claroglobal-vod.clarovideo.net/licenser/getlicense|User-Agent=' + USER_AGENT + '|{"token":"24c735c1f0aa11d9f8fc56dd86c3fcb1","device_id":"beac6d8fdd97a5e184ace84f9988a0fc","widevineBody":"b{SSM}"}|')
        list_item.setProperty('inputstream.adaptive.license_key', 'https://widevine-claroglobal-vod.clarovideo.net/licenser/getlicense|Content-Type=&User-Agent=' + USER_AGENT + '|{"token":"' + token + '","device_id":"' + device_id + '","material_id":"' + material_id + '","widevineBody":"b{SSM}"}|')
        list_item.setProperty('inputstream.adaptive.server_certificate', server_certificate);
        list_item.setProperty('inputstream.adaptive.manifest_type', 'mpd')
        list_item.setProperty('inputstream', 'inputstream.adaptive')
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
    # Python3 migrated
    #
    def getOkru (self, vid, isLive):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.2989.0 Safari/537.36"
        if not isLive:
            channelUrl = "https://ok.ru/video/" + vid
            html = self.getRequest(channelUrl, "", USER_AGENT)

            #
            # Unscape HTML
            #
            html = BeautifulSoup(html, 'html.parser')
            unscapeHtml = str(html).replace("\\", "")

            # Get the URL
            m = re.findall (r'\{"name":"([^"]+)","url":"([^"]+)"', unscapeHtml)
            if m:
                for m_element in m:
                    if m_element[0] == "sd": #hd
                        u = m_element[1].replace("%3B", ";").replace("u0026", "&")
                    elif m_element[0] == "low": 
                        u = m_element[1].replace("%3B", ";").replace("u0026", "&")
            
        else:
            channelUrl = "https://ok.ru/live/" + vid
            html = self.getRequest(channelUrl, "", USER_AGENT)

            #
            # Unscape HTML
            #
            html = BeautifulSoup(html, 'html.parser')
            unscapeHtml = str(html).replace("\\", "")
            print (unscapeHtml)

            # Get the URL
            m = re.findall (r'"hlsMasterPlaylistUrl":"([^"]+)"', unscapeHtml)
            if m:
                u = m[0].replace("%3B", ";").replace("u0026", "&")

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
            print ("URL: " + referUrl + " --> " + urllib.parse.unquote(referUrl))
            html = self.getRequest("http://kastream.biz/embed.php?file=" + videoContentId, urllib.parse.unquote(referUrl), USER_AGENT)
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
        print ("URL: " + referUrl + " --> " + urllib.parse.unquote(referUrl))
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.parse.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 
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
                u = wsUrl.group(1) + '|Referer=' + urllib.parse.unquote(referUrl) + '&User-Agent=' + USER_AGENT
                print ("Final URL: " + u)
                return u 

    #
    # tl.tv support
    #
    def getTlTv (self, channelId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4289.0 Safari/537.36"
        channelUrl = base64.b64decode("aHR0cHM6Ly90ZWxlcml1bS50dg==").decode('utf-8') + "/embed/" + channelId + ".html"
        headers = {
            'User-Agent':USER_AGENT, 
            'Referer':urllib.parse.unquote(channelUrl), 
            'Accept':"application/json, text/javascript, */*; q=0.01", 
            'Accept-Language':'pl,en-US;q=0.7,en;q=0.3',
            'X-Requested-With':'XMLHttpRequest'
        } 
        
        cookies = {'elVolumen': '100',
               '__ga':'100'}

        # Create URL channel
        datenow = datetime.utcnow().replace(second=0, microsecond=0)
        datenow = datenow + timedelta(days=1)
        epoch = datetime(1970, 1, 1)
        timer = (datenow - epoch).total_seconds()
        datetoken = int(timer) * 1000
        jsonUrl = base64.b64decode("aHR0cHM6Ly90ZWxlcml1bS50dg==").decode('utf-8') + "/streams/" + channelId + "/" + str(datetoken) + ".json"
        if self.enabledebug: print ("jsonUrl: " + jsonUrl)

        # Get the Token URL 
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(jsonUrl, headers=headers, cookies=cookies, verify=False).content
        if self.enabledebug: print ("html: " + html.decode('utf-8'))
        tokens = json.loads(html)
        cdn = tokens['url']
        nexturl = base64.b64decode("aHR0cHM6Ly90ZWxlcml1bS50dg==").decode('utf-8') + tokens['tokenurl']
        if self.enabledebug: print ("nexturl: " + nexturl)
        
        # Get the final Token
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(nexturl, headers=headers, cookies=cookies, verify=False).content
        tokens = json.loads(html)
        tokenHtml = tokens[10][::-1]
        if self.enabledebug: print ("tokenHtml: " + tokenHtml)
        
        # Parse the final URL
        stream = 'https:{0}{1}|Referer={2}&User-Agent={3}&Origin={4}&Sec-Fetch-Mode=cors'
        u = stream.format(cdn, tokenHtml, urllib.parse.quote(channelUrl, safe=''), USER_AGENT, base64.b64decode('aHR0cHM6Ly90ZWxlcml1bS50dg=='))
        return u

    #
    # wstream.to support
    #
    def getWstream(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3730.0 Safari/537.36"
        channelUrl = "https://wstream.to/embed/" + videoContentId
        headers = {'User-Agent':USER_AGENT, 'Referer':urllib.parse.unquote(referUrl), 'Accept':"*/*", 'Accept-Encoding':'deflate', 'Accept-Language':'Accept-Language: en-US,en;q=0.9,es;q=0.8,zh-CN;q=0.7,zh;q=0.6,gl;q=ru;q=0.4'} 

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(channelUrl, headers=headers)

        dataUnpack = re.compile('(eval\(function\(p,a,c,k,e,d\).*)').search(html.text)
        if (dataUnpack):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(dataUnpack.group(1))
            print ("unPack: " + unPack)

            # Get the URL
            m = re.compile('source:"(.+?)"').search(unPack)
            streamUrl = ""
            if (m):
                streamUrl = m.group(1)

            # Parse the final URL
            stream = '{0}|Referer={1}&User-Agent={2}'
            u = stream.format(streamUrl, urllib.parse.quote(channelUrl, safe=''), USER_AGENT)
            return u

    #
    # getXyzembed379 support
    #
    def getXyzembed379(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4242.0 Safari/537.36"
        channelUrl = "https://xyzembed379.net/embed/" + videoContentId
        headers = {
            'authority': 'xyzembed379.net',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENT, 
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            'referer': urllib.parse.unquote(referUrl),
            'accept-language':'en-US,en;q=0.9,es-CO;q=0.8,es;q=0.7'
        } 

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(channelUrl, headers=headers)
        
        dataUnpack = re.compile('(eval\(function\(p,a,c,k,e,d\).*)').search(html.text)
        if (dataUnpack):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(dataUnpack.group(1))
            print ("unpack" + unPack)

            # Get the URL
            m = re.compile('source:"(.+?)"').search(unPack)
            streamUrl = ""
            if (m):
                streamUrl = m.group(1)

            # Parse the final URL
            stream = '{0}|Referer={1}&User-Agent={2}'
            u = stream.format(streamUrl, urllib.parse.quote(channelUrl, safe=''), USER_AGENT)
            return u

    #
    # wigistream.to support
    #
    def getWigistream(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4680.2 Safari/537.36"
        channelUrl = "https://ragnarp.net/embed/" + videoContentId

        headers = {
            'authority': 'ragnarp.net',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENT, 
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            'referer': urllib.parse.unquote(referUrl),
            'accept-language':'en-US,en;q=0.9,es-CO;q=0.8,es;q=0.7'
        } 

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(channelUrl, headers=headers)

        dataUnpack = re.compile('(eval\(function\(p,a,c,k,e,d\).*)').search(html.text)
        if (dataUnpack):
            unPacker = jsUnpack.jsUnpacker()
            unPack = unPacker.unpack(dataUnpack.group(1))
            print ("unpack" + unPack)

            # Get the URL
            m = re.compile('var src="(.+?)"').search(unPack)
            streamUrl = ""
            if (m):
                streamUrl = m.group(1)

            # Parse the final URL
            stream = '{0}|Referer={1}&User-Agent={2}'
            u = stream.format(streamUrl, urllib.parse.quote(channelUrl, safe=''), USER_AGENT)
            return u


    #
    # pkcast123.me support
    #
    def getPkcast123(self, videoContentId, referUrl):
        USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4680.2 Safari/537.36"
        channelUrl = "https://www.pkcast123.me/footy.php?player=desktop&live=" + videoContentId + "&vw=541&vh=400"

        headers = {
            'authority': 'https://www.pkcast123.me',
            'upgrade-insecure-requests': '1',
            'user-agent': USER_AGENT, 
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-dest': 'iframe',
            'accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
            'referer': urllib.parse.unquote(referUrl),
            'accept-language':'en-US,en;q=0.9,es-CO;q=0.8,es;q=0.7'
        } 

        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        html = requests.get(channelUrl, headers=headers)

        # Get the URL
        m = re.compile('\"h\",\"t\",\"t\",\"p(.*)]').search(html.text)
        streamUrl = ""
        if (m):
            print ("m.group(1)>>" + m.group(1))
            streamUrl = m.group(1)
            streamUrl = "http" + streamUrl.replace('","',"").replace('\\', '')
            print (streamUrl)

        # Parse the final URL
        stream = '{0}|Referer={1}&User-Agent={2}'
        u = stream.format(streamUrl, urllib.parse.quote(channelUrl, safe=''), USER_AGENT)
        return u