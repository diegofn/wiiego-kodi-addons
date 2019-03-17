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
# *  based on https://github.com/jsergio123/script.module.resolveurl/blob/master/lib/resolveurl/plugins/waaw.py
# */
from StringIO import StringIO
import json
import re
import base64
import urllib
import urllib2
import random

__name__ = 'hqq'

class hqqResolver():
    def request(self, url, headers={}):
        print('request: %s' % url)
        req = urllib2.Request(url, headers=headers)
        try:
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
        except urllib2.HTTPError, error:
            data=error.read()
        print('len(data) %s' % len(data))
        return data
    
    def resolve(self, media_id):
        user_agent = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/533.4 (KHTML, like Gecko) Chrome/5.0.375.127 Large Screen Safari/533.4 GoogleTV/162671'
        headers = { 'User-Agent': user_agent
                }

        web_url = "https://hqq.tv/player/embed_player.php?vid=%s" % media_id
        html = self.request(web_url, headers)
        
        if html:
            try:
                
                # 
                # Get IP
                #
                alea = str(random.random())[2:]
                
                headers.update({
                        'Referer': web_url
                    })

                jsonInfo = self.request("https://hqq.tv/player/ip.php?type=json&rand=" + alea, headers=headers)
                jsonIp = json.loads(jsonInfo)['ip']
                 
                #
                # Unwise first page
                #
                wise = re.search('''<script>\s*;?(eval.*?)</script>''', html,
                                 re.DOTALL | re.I).groups()[0]
                data_unwise = self.jswise(wise).replace("\\", "")
                try:
                    url = re.search('self\.location\.replace\("([^)]+)\)', data_unwise, re.I).groups()[0]
                    url = url.replace('"+rand+"', alea)
                    url = url.replace('"+data.ip+"', jsonIp)
                    url = url.replace('"+need_captcha+"', '0')
                    url = url.replace('"+token', '')

                except:
                    url = ""

                #
                # Get sec/player/embeb_player
                #
                player_url = "https://hqq.tv" + url
                data_player = self.request(player_url, headers=headers)
                data_unescape = re.findall('document.write\(unescape\("([^"]+)"', data_player)
                # print "data_player: " + data_player
                data = ""
                for d in data_unescape:
                    data += urllib.unquote(d)

                #
                # Find variables
                #
                at = re.search('var at = "([^"]+)', data, re.I).groups()[0]
                var_link_1 = re.search('&link_1=\\"\+encodeURIComponent\(([^)]+)', data, re.I).groups()[0]
                var_server_2 = re.search('&server_2=\\"\+encodeURIComponent\(([^)]+)', data, re.I).groups()[0]
                vid = re.search('&vid=\\"\+encodeURIComponent\(\\"([^"]+)', data, re.I).groups()[0]
                ext = '.mp4.m3u8'
                # print('vars>>> %s %s %s %s' % (at, var_link_1, var_server_2, vid))

                #
                # Unwise data_player
                #
                data_unwise_player = ""
                wise = ""
                wise = re.search('''<script>\s*;?(eval.*?)</script>''', data_player,
                                 re.DOTALL | re.I)
                if wise:
                    data_unwise_player = self.jswise(wise.group(1)).replace("\\", "")

                # print "data_unwise_player: " + data_unwise_player
                variables = re.findall('var ([a-zA-Z0-9]+) = "([^"]+)";', data_unwise_player)
                for name, value in variables:
                    # print ("%s %s" % (name, value))
                    if name == var_link_1: link_1 = value
                    if name == var_server_2: server_2 = value

                #
                # Get get_md5.php
                #
                link_m3u8 = 'https://hqq.tv/player/get_md5.php?ver=2&at=%s&adb=0&b=1&link_1=%s&server_2=%s&vid=%s&ext=%s' % (at, link_1, server_2, vid, ext)
                print ("link_m3u8: " + link_m3u8)
                return link_m3u8 + '|Referer=' + urllib.quote(player_url, safe='') + '&User-Agent=' + user_agent

            except Exception as e:
                print str(e)

    def tb(self, b_m3u8_2):
        j = 0
        s2 = ""
        while j < len(b_m3u8_2):
            s2 += "\\u0" + b_m3u8_2[j:(j + 3)]
            j += 3

        return s2.decode('unicode-escape').encode('ASCII', 'ignore')

    ## loop2unobfuscated
    def jswise(self, wise):
        while True:
            wise = re.search("var\s.+?\('([^']+)','([^']+)','([^']+)','([^']+)'\)", wise, re.DOTALL)
            if not wise: break
            ret = wise = self.js_wise(wise.groups())

        return ret

    ## js2python
    def js_wise(self, wise):
        w, i, s, e = wise

        v0 = 0;
        v1 = 0;
        v2 = 0
        v3 = [];
        v4 = []

        while True:
            if v0 < 5:
                v4.append(w[v0])
            elif v0 < len(w):
                v3.append(w[v0])
            v0 += 1
            if v1 < 5:
                v4.append(i[v1])
            elif v1 < len(i):
                v3.append(i[v1])
            v1 += 1
            if v2 < 5:
                v4.append(s[v2])
            elif v2 < len(s):
                v3.append(s[v2])
            v2 += 1
            if len(w) + len(i) + len(s) + len(e) == len(v3) + len(v4) + len(e): break

        v5 = "".join(v3);
        v6 = "".join(v4)
        v1 = 0
        v7 = []

        for v0 in range(0, len(v3), 2):
            v8 = -1
            if ord(v6[v1]) % 2: v8 = 1
            v7.append(chr(int(v5[v0:v0 + 2], 36) - v8))
            v1 += 1
            if v1 >= len(v4): v1 = 0

        return "".join(v7)
