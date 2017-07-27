'''
    urlresolver XBMC Addon
    Copyright (C) 2016 Gujal

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''
import re
from urlresolver import common
from urlresolver.plugins.lib import helpers
from urlresolver.resolver import UrlResolver, ResolverError

class HClipsResolver(UrlResolver):
    name = 'hclips'
    domains = ['hclips.com']
    pattern = '(?://|\.)(hclips\.com)/(?:embed|videos)/(?:.+?\:\d+\:)?(\d+)'
    pattern2 = '(?://|\.)(hclips\.com)/videos/([\-\w]+)'
    
    def __init__(self):
        self.net = common.Net()

    def get_media_url(self, host, media_id):
        headers = {'User-Agent': common.RAND_UA}
        web_url = self.get_url(host, media_id)
        
        if not media_id.isdigit():
            html = self.net.http_GET(web_url, headers=headers).content
            if html:
                try:
                    web_url = re.search("""<iframe\s*width=['"]\d+['"]\s*height=['"]\d+['"]\s*src=['"](http:\/\/www\.hclips\.com\/embed\/(\d+))""", html).groups()[0]
                    
                except:
                    raise ResolverError('File not found')
            else: 
                raise ResolverError('File not found')

        html2 = self.net.http_GET(web_url, headers=headers).content
        if html2:
            sources = re.findall(''''label['"]:.+?,['"]file['"]:\s*['"](?P<url>[^'"]+)['"],['"]type['"]:\s*['"](?P<label>[^'"]+)''', html2, re.DOTALL)
            if sources:
                sources = [(i[1], i[0]) for i in sources]
                return self.net.http_GET(helpers.pick_source(sources), headers=headers).get_url() + helpers.append_headers(headers)
                
        raise ResolverError('File not found')
        
    def get_host_and_id(self, url):
        r = re.search(self.pattern, url, re.I)
        r = r if r else re.search(self.pattern2, url, re.I)
        if r: 
            return r.groups()
        else:
            return False
    
    def get_url(self, host, media_id):
        if not media_id.isdigit():
            return self._default_get_url(host, media_id, template='https://www.{host}/videos/{media_id}')
        else:
            return self._default_get_url(host, media_id, template='https://www.{host}/embed/{media_id}')
            
    def valid_url(self, url, host):
        return re.search(self.pattern, url, re.I) or re.search(self.pattern2, url, re.I) or self.name in host
        
    @classmethod
    def _is_enabled(cls):
        return True