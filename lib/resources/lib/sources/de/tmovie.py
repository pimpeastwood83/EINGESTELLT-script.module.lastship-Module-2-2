# -*- coding: utf-8 -*-

"""
    Lastship Add-on (C) 2017
    Credits to Exodus and Covenant; our thanks go to their creators

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import re

from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['tmovie.to']
        self.base_link = ' https://tmovie.to'
        self.search = self.base_link + '/search?keyword=%s'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            import pydevd
            pydevd.settrace('localhost', port=12345, stdoutToServer=True, stderrToServer=True)
            sHtmlContent = self.scraper.get(self.search % localtitle).content

            a = dom_parser.parse_dom(sHtmlContent, 'ul', attrs={'class': 'rig'})
            movie = dom_parser.parse_dom(a, 'li')
            url = self.base_link + dom_parser.parse_dom(movie[0], 'a')[0].attrs['href']

            return url

        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            sHtmlContent = self.scraper.get(self.search % localtvshowtitle).content

            a = dom_parser.parse_dom(sHtmlContent, 'ul', attrs={'class': 'rig'})
            movies = dom_parser.parse_dom(a, 'li')
            nameUrlTuples = [(dom_parser.parse_dom(i, 'span', attrs={'class': 'name'})[0].content, self.base_link + dom_parser.parse_dom(i, 'a')[0].attrs['href']) for i in movies]

            return nameUrlTuples
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            url = [i[1] for i in url if season in i[0]][0]

            return (episode, url)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            link = url if isinstance(url, str) else url[1]

            sHtmlContent = self.scraper.get(link).content

            a = dom_parser.parse_dom(sHtmlContent, 'li', attrs={'class': 'list-group-item'})
            if re.search('staffel', link, re.IGNORECASE):
                r = [dom_parser.parse_dom(i, 'button') for i in a]

                quality = dom_parser.parse_dom(sHtmlContent, 'div', attrs={'style': 'font-size:10px;'})
                quality = [i.content for i in dom_parser.parse_dom(quality[1], 'span') if not re.search('quality', i.content, re.IGNORECASE)][0]

                tuple = [[(str(x.attrs['data-seq']), quality) for x in i if url[0] in x.content][0] for i in r]
            else:
                r = [dom_parser.parse_dom(i, 'button')[0] for i in a]
                tuple = [(i.attrs['data-seq'], i.content) for i in r]

            for record in tuple:
                temp = self.__getLink(link + '/' + record[0])
                valid, host = source_utils.is_host_valid(temp, hostDict)
                if not valid: continue
                sources.append({'source': host, 'quality': 'HD' if 'HD' in record[1] else 'SD', 'language': 'de', 'url': temp, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def __getLink(self, url):
        sHtmlContent = self.scraper.get(url).content
        a = dom_parser.parse_dom(sHtmlContent, 'iframe', attrs={'class': 'fr'})[0]

        return a.attrs['src']

    def resolve(self, url):
        return url
