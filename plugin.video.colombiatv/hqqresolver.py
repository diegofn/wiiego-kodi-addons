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

    def _decode2(self, file_url):
        def K12K(a, typ='b'):
            codec_a = ["G", "L", "M", "N", "Z", "o", "I", "t", "V", "y", "x", "p", "R", "m", "z", "u",
                       "D", "7", "W", "v", "Q", "n", "e", "0", "b", "="]
            codec_b = ["2", "6", "i", "k", "8", "X", "J", "B", "a", "s", "d", "H", "w", "f", "T", "3",
                       "l", "c", "5", "Y", "g", "1", "4", "9", "U", "A"]
            if 'd' == typ:
                tmp = codec_a
                codec_a = codec_b
                codec_b = tmp
            idx = 0
            while idx < len(codec_a):
                a = a.replace(codec_a[idx], "___")
                a = a.replace(codec_b[idx], codec_a[idx])
                a = a.replace("___", codec_b[idx])
                idx += 1
            return a

        def _xc13(_arg1):
            _lg27 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            _local2 = ""
            _local3 = [0, 0, 0, 0]
            _local4 = [0, 0, 0]
            _local5 = 0
            while _local5 < len(_arg1):
                _local6 = 0
                while _local6 < 4 and (_local5 + _local6) < len(_arg1):
                    _local3[_local6] = _lg27.find(_arg1[_local5 + _local6])
                    _local6 += 1
                _local4[0] = ((_local3[0] << 2) + ((_local3[1] & 48) >> 4))
                _local4[1] = (((_local3[1] & 15) << 4) + ((_local3[2] & 60) >> 2))
                _local4[2] = (((_local3[2] & 3) << 6) + _local3[3])

                _local7 = 0
                while _local7 < len(_local4):
                    if _local3[_local7 + 1] == 64:
                        break
                    _local2 += chr(_local4[_local7])
                    _local7 += 1
                _local5 += 4
            return _local2

        return _xc13(K12K(file_url, 'e'))               

    def _decode3(self, w, i, s, e):
        var1 = 0
        var2 = 0
        var3 = 0
        var4 = []
        var5 = []
        while (True):
            if (var1 < 5):
                var5.append(w[var1])
            elif (var1 < len(w)):
                var4.append(w[var1])
            var1 += 1
            if (var2 < 5):
                var5.append(i[var2])
            elif (var2 < len(i)):
                var4.append(i[var2])
            var2 += 1
            if (var3 < 5):
                var5.append(s[var3])
            elif (var3 < len(s)):
                var4.append(s[var3])
            var3 += 1
            if (len(w) + len(i) + len(s) + len(e) == len(var4) + len(var5) + len(e)):
                break
        var6 = ''.join(var4)
        var7 = ''.join(var5)
        var2 = 0
        result = []
        for var1 in range(0, len(var4), 2):
            ll11 = -1
            if (ord(var7[var2]) % 2):
                ll11 = 1
            result.append(chr(int(var6[var1:var1 + 2], 36) - ll11))
            var2 += 1
            if (var2 >= len(var5)):
                var2 = 0
        return ''.join(result)

    def _decode_data(self, data):
        valuesPattern = r";}\('(\w+)','(\w*)','(\w*)','(\w*)'\)\)"
        values = re.search(valuesPattern, data, re.DOTALL)
        return self._decode3(values.group(1), values.group(2), values.group(3), values.group(4))

    def resolve(self, vid):
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1 (KHTML, like Gecko) CriOS/57.0.2987.137 Mobile/13G34 Safari/601.1.46'
        headers = { 'User-Agent': user_agent,
                    'Host' : 'hqq.tv',
                    'Referer': 'https://hqq.tv/player/embed_player.php?vid=' + vid + '&autoplay=none',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Content-Type': 'text/html; charset=utf-8'}
        player_url = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % vid
        data = self.request(player_url, headers)

        data = self._decode_data(data)
        data = self._decode_data(data)
        code_crypt = data.split(';; ')
        data = self._decode_data(code_crypt[1])

        if data:
            jsonInfo = self.request("http://hqq.tv/player/ip.php?type=json", headers)
            jsonIp = json.loads(jsonInfo)['ip']

            at = re.search(r'var at *= *"(\w+)";', data, re.DOTALL)
            http_referer = re.search('var http_referer *= *"([^"]+)";', data, re.DOTALL)
            
            if jsonIp and at:
                get_data = {'iss': jsonIp, 'vid': vid, 'at': at.group(1), 'autoplayed': 'on', 'referer': 'on',
                            'http_referer': http_referer.group(1), 'pass': '', 'embed_from' : '', 'need_captcha' : '0',
                            'hash_from' : ''
                            }

                #curl 'https://hqq.tv/sec/player/embed_player.php?iss=MTkwLjI2LjE3OC4xNQ==&vid=233207256242243226255237262241234263194271217271255&at=7922b7e58d64850607bf311522dc6d40&autoplayed=yes&referer=on&http_referer=aHR0cDovL3d3dy5jYXJ0ZWx0di5uZXQvQ29udHJhLUVsLVRpZW1wby82MC5odG1s&pass=&embed_from=&need_captcha=0&hash_from=7922b7e58d64850607bf311522dc6d40' 
                # \-XGET \-H 'Referer: https://hqq.tv/player/embed_player.php?vid=233207256242243226255237262241234263194271217271255&autoplay=none&hash_from=7922b7e58d64850607bf311522dc6d40' 
                # \-H 'User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13G34 Safari/601.1' 
                # \-H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                data = urllib.unquote(self.request("http://hqq.tv/sec/player/embed_player.php?" +
                                                   urllib.urlencode(get_data), headers))

                at = re.search(r'var\s*at\s*=\s*"([^"]*?)"', data)
                l = re.search(r'link_1: ([a-zA-Z]+), server_1: ([a-zA-Z]+)', data)
                
                data = self._decode_data(data)
                data = self._decode_data(data)
                code_crypt = data.split(';; ')
                data = self._decode_data(code_crypt[1])
                
                vid_server = re.search(r'var ' + l.group(2) + ' = "([^"]+)"', data).group(1)
                vid_link = re.search(r'var ' + l.group(1) + ' = "([^"]+)"', data).group(1)

                if vid_server and vid_link and at:
                    get_data = {'server_1': vid_server, 'link_1': vid_link, 'at': at.group(1), 'adb': '0/',
                                'b': '1', 'vid': vid }
                    headers['x-requested-with'] = 'XMLHttpRequest'
                    data = self.request("http://hqq.tv/player/get_md5.php?" + urllib.urlencode(get_data), headers)
                    jsonData = json.loads(data)
                    encodedm3u = jsonData['file']
                    decodedm3u = self._decode2(encodedm3u.replace('#', ''))
                    decodedm3u = decodedm3u.replace("?socket", ".mp4.m3u8")

                    fake_agent = user_agent
                    return decodedm3u  + '|' + fake_agent

        return None