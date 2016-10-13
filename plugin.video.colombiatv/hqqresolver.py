# -*- coding: UTF-8 -*-
# *  GNU General Public License for more details.
# *
# *
# *  You should have received a copy of the GNU General Public License
# *  along with this program; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html
# *
# *
# *  based on https://gitorious.org/iptv-pl-dla-openpli/ urlresolver
# */
from StringIO import StringIO
import json
import re
import base64
import urllib
import urllib2


__name__ = 'hqq'
UA = 'Mozilla/6.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.5) Gecko/2008092417 Firefox/3.0.3'

class hqqResolver():
    def request(self, url, headers={}):
        print('request: %s' % url)
        req = urllib2.Request(url, headers=headers)
        req.add_header('User-Agent', UA)
        try:
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
        except urllib2.HTTPError, error:
            data=error.read()
        print('len(data) %s' % len(data))
        return data

    def post(self, url, data, headers={}):
        postdata = urllib.urlencode(data)
        req = urllib2.Request(url, postdata, headers)
        req.add_header('User-Agent', UA)
        try:
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
        except urllib2.HTTPError, error:
            data=error.read()
        print('len(data) %s' % len(data))
        return data
        
    def supports(self, url):
        return self._regex(url) is not None


    def _decode(self, data):
        def O1l(string):
            ret = ""
            i = len(string) - 1
            while i >= 0:
                ret += string[i]
                i -= 1
            return ret

        def l0I(string):
            enc = ""
            dec = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
            i = 0
            while True:
                h1 = dec.find(string[i])
                i += 1
                h2 = dec.find(string[i])
                i += 1
                h3 = dec.find(string[i])
                i += 1
                h4 = dec.find(string[i])
                i += 1
                bits = h1 << 18 | h2 << 12 | h3 << 6 | h4
                o1 = bits >> 16 & 0xff
                o2 = bits >> 8 & 0xff
                o3 = bits & 0xff
                if h3 == 64:
                    enc += unichr(o1)
                else:
                    if h4 == 64:
                        enc += unichr(o1) + unichr(o2)
                    else:
                        enc += unichr(o1) + unichr(o2) + unichr(o3)
                if i >= len(string):
                    break
            return enc

        escape = re.search("var _escape=\'([^\']+)", l0I(O1l(data))).group(1)
        return escape.replace('%', '\\').decode('unicode-escape')


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


    def resolve(self, vid):
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Content-Type': 'text/html; charset=utf-8', 'Referer': 'http://hqq.tv/', 'X-Requested-With':'XMLHttpRequest'}
        player_url = "http://hqq.tv/player/embed_player.php?vid=%s&autoplay=no" % vid
        data = self.request(player_url, headers)
        b64enc = re.search('base64([^\"]+)', data, re.DOTALL)
        b64dec = b64enc and base64.decodestring(b64enc.group(1))
        enc = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
        if enc:
            data = re.findall('<input name="([^"]+?)" [^>]+? value="([^"]+?)">', self._decode(enc))
            post_data = {}
            for idx in range(len(data)):
                post_data[data[idx][0]] = data[idx][1]
            data = self.post(player_url, post_data, headers)
            b64enc = re.search('base64([^\"]+)', data, re.DOTALL)
            b64dec = b64enc and base64.decodestring(b64enc.group(1))
            enc = b64dec and re.search("\'([^']+)\'", b64dec).group(1)
            if enc:
                data = re.findall('<input name="([^"]+?)" [^>]+? value="([^"]*)">', self._decode(enc))
                post_data = {}
                for idx in range(len(data)):
                    post_data[data[idx][0]] = data[idx][1]
                data = urllib.unquote(self.request("http://hqq.tv/sec/player/embed_player.php?" +
                                                   urllib.urlencode(post_data), headers))
                servervarname=re.search('server_1: ([^,]+)',re.findall('md5.*',data)[0]).group(1)
                linkvarname=re.search('link_1: ([^,]+)',re.findall('md5.*',data)[0]).group(1)

                vid_server = re.search(r'var\s*%s\s*=\s*"([^"]*?)"' % servervarname, data)
                vid_link = re.search(r'var\s*%s\s*=\s*"([^"]*?)"' % linkvarname, data)
                at = re.search(r'var\s*at\s*=\s*"([^"]*?)"', data)
                if vid_server and vid_link and at:
                    get_data = {'server_1': vid_server.group(1),
                                'link_1': re.sub(r'\?socket=?$', '.mp4.m3u8', vid_link.group(1)),
                                'at': at.group(1),
                                'adb': '1/',
                                'b' : '1',
                                'vid' : vid
                               }
                    data = self.request("http://hqq.tv/player/get_md5.php?" + \
                           urllib.urlencode(get_data), headers)
                    jsondata = json.loads(data)
                    encodedm3u = jsondata['file']
                    decodedm3u=self._decode2(encodedm3u.replace('\\', ''))

                    agent = 'User-Agent=Mozilla/5.0 (iPhone; CPU iPhone OS 5_0_1 like Mac OS X)'
                    return decodedm3u+'|'+agent
        
        return None

    def _regex(self, url):
        match = re.search("(hqq|netu)\.tv/watch_video\.php\?v=(?P<vid>[0-9A-Z]+)", url)
        if match:
            return match
        match = re.search(r'(hqq|netu)\.tv/player/embed_player\.php\?vid=(?P<vid>[0-9A-Z]+)', url)
        if match:
            return match
        match = re.search(r'(hqq|netu)\.tv/player/hash\.php\?hash=\d+', url)
        if match:
            match = re.search(r'var\s+vid\s*=\s*\'(?P<vid>[^\']+)\'', urllib.unquote(self.request(url)))
            if match:
                return match
        b64enc = re.search(r'data:text/javascript\;charset\=utf\-8\;base64([^\"]+)', url)
        b64dec = b64enc and base64.decodestring(b64enc.group(1))
        enc = b64dec and re.search(r"\'([^']+)\'", b64dec).group(1)
        if enc:
            decoded = self._decode(enc)
            match = re.search(r'<input name="vid"[^>]+? value="(?P<vid>[^"]+?)">', decoded)
            if re.search(r'<form(.+?)action="[^"]*(hqq|netu)\.tv/player/embed_player\.php"[^>]*>',
                         decoded) and match:
                return match
        return None