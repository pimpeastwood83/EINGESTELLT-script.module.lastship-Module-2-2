# -*- coding: utf-8 -*-

import json
import urllib
import urlparse
import re
import base64
import hashlib
import requests
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['onlinefilme.to']
        self.base_link = 'http://onlinefilme.to/'
        self.movie_link= self.base_link + 'filme-online/'
        self.movie_link= self.base_link + 'serie-online/'
        self.search_link='suche/%s'
        

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
        
            # webseitet arbeitet mir org. titel. local titel führt zu verfälschung
            url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            print "print movie return url", url
                        
            return url
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            
            return 
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            return 
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:                
                return sources
            
            sHtmlContent = requests.get(url)
            #print "print onlinefilme source sHtmlContent", sHtmlContent

            
            pattern1= 'title="(.*)?">(.*)<\/span'
            hoster = re.compile(pattern1).findall(sHtmlContent.content)
            print "print onlinefilme pattern hoster",type(hoster),type(hoster[0]),hoster
            print "print declare hosterlist"
            
            aList=[]
            
            for i in hoster:
                item=i[0]
                print "print hoster item type", type(item),item
                aList.append(format(item))

            #print "print onlinefilme pattern hoster list",type(aList),type(aList[0]),aList,aList[0]
            
            pattern2="href='(.*play.*-stream)"
            streams = re.compile(pattern2).findall(sHtmlContent.content)
            print "print onlinefilme pattern streams",streams

            for x,y in map(None,aList,streams):
                url=requests.get(y).url
                source_quality=x.split("-")

                
                #print "print line split",type(source_quality),source_quality,source_quality[0],source_quality[1].lstrip()
                print "print streams redirect",source_quality,url


                if "HD" in source_quality[1]:
                    quality="720p"
                else:
                    quality="SD"

                # manual override.Qualität ist zu 99% SD
                sources.append({'source': source_quality[0], 'quality':'SD' , 'language': 'de', 'url': url, 'direct': False, 'debridonly': False})


            
            
            return sources
        except:
            return sources


    def resolve(self, url):
        return url

    def __search(self,titles, year):
        try:
            print "print onlinefilme search titles", titles
            t = [cleantitle.get(i) for i in set(titles) if i]
            #t = cleantitle.get(localtitle)
            print "print onlinefilme cleantitle & titles", t
        
            
            searchstring = base64.b64encode('search_term=%s&search_type=0&search_where=0&search_rating_start=1&search_rating_end=10&search_year_from=1900' % titles[0] )
            print "print onlinefilme base64", searchstring        
            sHtmlContent = client.request(urlparse.urljoin(self.base_link, self.search_link % searchstring))
            #print "print onlinefilme search sHtmlContent", sHtmlContent
    
            pattern= 'href="(.*?-stream)'
            r = re.compile(pattern).findall(sHtmlContent)

            print "print onlinefilme search aResult",r

            r = [(i, re.findall('\d{4}', i, )[0]) for i in r]
            print "print onlinefilme cleantitle 1",r
            r = sorted(r, key=lambda i: int(i[1]), reverse=True)  # with year > no year
            print "print onlinefilme cleantitle 2",r
            r = [x[0] for x in r if int(x[1]) == int(year)]
            print "print onlinefilme cleantitle 3",r
            url = str(r[0])
  
            
            
            return url

            
            
                        
        except:
            return
