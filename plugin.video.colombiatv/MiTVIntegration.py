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
import simplejson
import urllib3
import certifi
import json
import base64
from datetime import datetime
import time


# Base URL for all querys. 
DROPBOX_BASE_URL = "www.dropbox.com"

class MiTVIntegration():
    def __init__(self):
        #
        # Load EPG channels from file
        # 
        CHANNEL_URL = base64.b64decode("L3MvenQ1NXJzZDYxOXQydTV1L2VwZy5qc29uP2RsPTE=").decode('utf-8')
        self.url = "https://{0}{1}".format(DROPBOX_BASE_URL, CHANNEL_URL)

        #
        # Load the info in a JSON structure
        #
        http = urllib3.PoolManager(ca_certs=certifi.where())
        response = http.request('GET', self.url)
                
        self.epgChannels = simplejson.loads(response.data.decode('utf-8'))

        #
        # Load epg info
        #
        self.loadEPGInfo()
    
    
    def loadEPGInfo(self):
        #
        # Load the epg info from mi.tv
        #
        EPG_BASE = base64.b64decode("aHR0cDovL2FwaS5taS50di9lcGcvZ3VpZGUvdjMv").decode('utf-8')
        epg_url = EPG_BASE + datetime.now().strftime('%Y-%m-%d') + "?"

        for element in self.epgChannels["mitvEpg"]:
            epg_url += "channelId=" + element["mitvChannelId"] + "&"

        epg_url += "timeZoneOffset=-300"

        #
        # Load the info in a JSON structure
        #
        http = urllib3.PoolManager(ca_certs=certifi.where())
        response = http.request('GET', self.url)
        
        self.epgGuide = simplejson.loads(response.data.decode('utf-8'))


    def getChannelInfo(self, channelId):

        #
        # Find mitvChanneldId
        #
        mitvChannelId = 0
        for element in self.epgChannels["mitvEpg"]:
            if element["id"] == channelId:
                mitvChannelId = element["mitvChannelId"]
                break

        #
        # Create EPGInfo now and plot
        #
        if mitvChannelId != 0:
            for element in self.epgGuide:
                epg_now = []
                epg_plot = ""
                nowtime = time.mktime(datetime.now().timetuple()) * 1000
                ii = 0

                if element ["channelId"] == mitvChannelId:
                    for element_broadcast in element["broadcasts"]:  
                        #
                        # Set now guide
                        #
                        if nowtime >= element_broadcast["beginTimeMillis"] and nowtime <= element_broadcast["endTimeMillis"]:
                            epg_now = element_broadcast["program"]

                            if not "category" in epg_now:
                                epg_now["category"] = ""

                            ii = 1      

                        #
                        # Set plot info
                        #
                        if ii >= 1 and ii <= 3:
                            begintime = datetime.fromtimestamp(element_broadcast["beginTimeMillis"] / 1000).strftime('%H:%M')
                            if ii == 1:
                                epg_plot = "[COLOR blue]" + begintime + " " + element_broadcast["program"]["title"] + "[/COLOR][CR]"
                            else:
                                epg_plot += begintime + " " + element_broadcast["program"]["title"] + "[CR]"

                            ii += 1

                    #
                    # break if element ["channelId"] == mitvChannelId:
                    #
                    break
            
            return epg_now, epg_plot

        else:
            return None, None

    def getProgramInfo(self, programId):
        return "getChannelInfo: " + programId


#mitvEpg = MiTVIntegration()
#now, plot = mitvEpg.getChannelInfo("2")
#print ("Tag line: " + now["title"] if now["title"] else "")
#print ("Genre: " + now["category"] if now["category"] else "")
#print ("Tag: " + now["tags"][0] if now["tags"] else "")
#print ("Plot: " + plot if plot else "")