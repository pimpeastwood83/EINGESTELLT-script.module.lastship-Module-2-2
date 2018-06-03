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
import re, base64, urllib

from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_faultlog
from resources.lib.modules import cleantitle
from resources.lib.modules import client


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['onlinefilme.to']
        self.base_link = ' https://onlinefilme.to'
        self.search = 'search_term=%s&search_type=%s&search_where=0&search_rating_start=1&search_rating_end=10&search_year_from=%s&search_year_to=%s&search_sync_2=2'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            t = [cleantitle.get(i) for i in set(source_utils.aliases_to_array(aliases)) if i]
            t.append(cleantitle.get(title))
            t.append(cleantitle.get(localtitle))

            url = self.base_link + '/suche/' + base64.b64encode(self.search % (urllib.quote_plus(cleantitle.query(localtitle)),"1", year, year))
            content = client.request(url)
            links = self._getLinks(content)

            links = [i[1] for i in links if cleantitle.get(re.findall('\n(.*)\n', links[0][0])[0]) in t]

            return links[0]
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagSearch)
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            return self.base_link + '/suche/' + base64.b64encode(self.search % (urllib.quote_plus(cleantitle.query(localtvshowtitle)),"2", "1990", "2018"))
        except:
            source_faultlog.logFault(__name__,source_faultlog.tagSearch)
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            content = client.request(url)

            links = self._getLinks(content)

            temp = season + '. staffel'
            links = [i[1] for i in links if temp in i[0]]

            return (episode, links[0])
        except:
            source_faultlog.logFault(__name__,source_faultlog.tagSearch)
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            link = url if isinstance(url, unicode) else url[1]

            content = client.request(link)

            if not isinstance(url, unicode):
                temp = 'Episoden %s' % url[0]
                hoster = dom_parser.parse_dom(content, 'dd', attrs={'class': 'accordion-navigation'})
                hoster = [i for i in hoster if temp in i.content]
            else:
                hoster = dom_parser.parse_dom(content, 'div', attrs={'class': 'movie-links-holder'})[0]

            hoster = dom_parser.parse_dom(hoster, 'div', attrs={'class': 'panel'})
            hoster = [(dom_parser.parse_dom(i, 'span')[0].attrs['title'],dom_parser.parse_dom(i, 'a', attrs={'class': 'button'})[0].attrs['href']) for i in hoster]
            hoster = [(re.findall('(.*)\s-\s(.*)', i[0])[0], i[1]) for i in hoster]

            for hosterQuality, link in hoster:
                valid, host = source_utils.is_host_valid(hosterQuality[0], hostDict)
                if not valid: continue
                sources.append({'source': host, 'quality': 'HD' if 'HD' in hosterQuality[1] else 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            source_faultlog.logFault(__name__,source_faultlog.tagScrape)
            return sources

    def resolve(self, url):
        content = self.scraper.get(url)

        if self.domains[0] in content.url:
            content = dom_parser.parse_dom(content.content, 'div', attrs={'class': 'text-center'})
            content = [i for i in content if 'iframe' in i.content]
            url = dom_parser.parse_dom(content, 'a')[0].attrs['href']
        else:
            url = content.url

        return url

    def _getLinks(self, content):
        links = dom_parser.parse_dom(content, 'ul', attrs={'class': 'enable-hover-link'})
        links = dom_parser.parse_dom(links, 'a')
        return [(dom_parser.parse_dom(i, 'div', attrs={'class': 'title'})[0].content, i.attrs['href']) for i in links]
