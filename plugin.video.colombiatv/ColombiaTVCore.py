#/*
# *
# * ColombiaTV: ColombiaTV add-on for XBMC.
# *
# * Copyright (C) 2013-2014 Wiiego
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
        self.enabledebug = sys.modules["__main__"].enabledebug
        urllib2.install_opener(sys.modules["__main__"].opener)

        self.url = "https://" + BASE_URL + CHANNEL_URL + 'channels.json'

    # Return the URL from TV Channel
    def get_channel_list(self):
        req = urllib2.Request(self.url)
        f = urllib2.urlopen(req)
        result = simplejson.load(f)
        f.close()

        if self.enabledebug == True:
            print result['ColombiaTV']
        return result['ColombiaTV']

        
