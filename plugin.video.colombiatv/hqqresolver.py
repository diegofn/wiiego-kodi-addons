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
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/57.0.2987.137 Mobile/13G34 Safari/601.1.46'
        headers = { 'User-Agent': user_agent,
                    'Referer': 'https://hqq.watch/player/embed_player.php?vid=' + media_id}
        web_url = "https://hqq.watch/player/embed_player.php?vid=%s" % media_id
        html = self.request(web_url, headers)
        
        if html:
            try:
                wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', html,
                                 re.DOTALL | re.I).groups()[0]
                data_unwise = self.jswise(wise).replace("\\", "")
                try:
                    at = re.search('at=(\w+)', data_unwise, re.I).groups()[0]
                except:
                    at = ""
                try:
                    http_referer = re.search('http_referer=(.*?)&', data_unwise, re.I).groups()[0]
                except:
                    http_referer = ""

                player_url = "http://hqq.watch/sec/player/embed_player.php?iss=&vid=%s&at=%s&autoplayed=yes&referer=on&http_referer=%s&pass=&embed_from=&need_captcha=0&hash_from=&secured=0" % (
                media_id, at, http_referer)
                headers.update({'Referer': web_url})
                data_player = self.request(player_url, headers=headers)
                data_unescape = re.findall('document.write\(unescape\("([^"]+)"', data_player)
                data = ""
                for d in data_unescape:
                    data += urllib.unquote(d)

                data_unwise_player = ""
                wise = ""
                wise = re.search('''<script type=["']text/javascript["']>\s*;?(eval.*?)</script>''', data_player,
                                 re.DOTALL | re.I)
                if wise:
                    data_unwise_player = self.jswise(wise.group(1)).replace("\\", "")

                try:
                    vars_data = re.search('/player/get_md5.php",\s*\{(.*?)\}', data, re.DOTALL | re.I).groups()[0]
                except:
                    vars_data = ""
                matches = re.findall('\s*([^:]+):\s*([^,]*)[,"]', vars_data)
                params = {}
                for key, value in matches:
                    if key == "adb":
                        params[key] = "0/"
                    elif '"' in value:
                        params[key] = value.replace('"', '')
                    else:
                        try:
                            value_var = re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data, re.I).groups()[0]
                        except:
                            value_var = ""
                        if not value_var and data_unwise_player:
                            try:
                                value_var = \
                                re.search('var\s*%s\s*=\s*"([^"]+)"' % value, data_unwise_player, re.I).groups()[0]
                            except:
                                value_var = ""
                        params[key] = value_var

                params = urllib.urlencode(params)
                headers.update({'X-Requested-With': 'XMLHttpRequest', 'Referer': player_url})
                data = ""
                data = self.request("http://hqq.watch/player/get_md5.php?" + params, headers=headers)
                url_data = json.loads(data)
                media_url = self.tb(url_data["obf_link"].replace("#", "")) + ".mp4.m3u8"

                if media_url:
                    del headers['X-Requested-With']
                    headers.update({'Origin': 'https://hqq.watch'})
                    return media_url 

            except Exception as e:
                print str(e)
                raise ResolverError(e)

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
