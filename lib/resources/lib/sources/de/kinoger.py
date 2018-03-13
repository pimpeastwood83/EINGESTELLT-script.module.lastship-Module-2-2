# -*- coding: utf-8 -*-

import json
import urllib
import urlparse
import re
import base64
import hashlib

from resources.lib.modules import client
from resources.lib.modules import pyaes
from resources.lib.modules import cfscrape

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['kinoger.com']
        self.base_link = 'http://kinoger.com/'
        self.movie_link= self.base_link + 'movies?perPage=54'
        self.movie_link= self.base_link + 'seasons?perPage=54'
        self.search=self.base_link + 'index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&story=%s'
        self.scraper=cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            print "print movie entry to search", imdb,title,localtitle,aliases,year
            url = self.__search(localtitle,year)
            print "print movie return url", url

            # Hack für die Suche, needs testing
            if not url:
                for aliases in aliases:
                    print "print aliases", aliases['title']
                    if aliases['country']=='de':
                        url = self.__search(aliases['title'],year)
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
            
            sHtmlContent=self.scraper.get(url).content
            #print "print kinoger film sources content", sHtmlContent          
            pattern = '''(hdgo.show[^>].*?|<iframe[^>]src=")(http[^"']+)'''
            link = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
            #print "print source aResult pattern", type(aResult),aResult

            
            
         
            for dummy,link in link:
                print "print link in aResult", link
                
                
                if 'mail' in link:
                    sources.append({'source': 'MyMail.ru', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'ok.ru' in link:
                    sources.append({'source': 'OK.ru', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': True, 'debridonly': False})
                elif 'rapidvideo' in link:
                    sources.append({'source': 'rapidvideo.com', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'getvi' in link:
                    sources.append({'source': 'getvi', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'streamcloud' in link:
                    sources.append({'source': 'streamcloud.com', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'hdgo' in link:
                    print "print hdgo in link", link
                    
                    request=client.request(link,referer=link)

                    #print "print hdgoclient request)",request
                    pattern = '<iframe[^>]src="//([^"]+)'                    
                    request = re.compile(pattern, re.DOTALL).findall(request)
                    #print "print hdgoclient link referer request, r[0]",request, request[0]
                    
                    #print "print hdgoclient referer"
                    request=client.request('http://' + request[0],referer=link)
                    
                    #print "print hdgoclient request 2",request
                    pattern = "url:[^>]'([^']+)"
                    request = re.compile(pattern, re.DOTALL).findall(request)
                    #print "print hdgoclient final link ",request

                    for i,stream in enumerate(request):
                        
                        if i==2:
                            sources.append({'source': 'hdgo.cc', 'quality': 'HD', 'language': 'de', 'url': stream + '|Referer=' + link, 'direct': True, 'debridonly': False})
                        elif i==3:
                            sources.append({'source': 'hdgo.cc', 'quality': '1080p', 'language': 'de', 'url': stream + '|Referer=' + link, 'direct': True, 'debridonly': False})
                        else:
                            sources.append({'source': 'hdgo.cc', 'quality': 'SD', 'language': 'de', 'url': stream + '|Referer=' + link, 'direct': True, 'debridonly': False})
                else:
                    sources.append({'source': 'CDN', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': True, 'debridonly': False})
                    
            return sources
        except:
            return sources


    def resolve(self, url):
        return url

    def __search(self, localtitle,year):
        try:

            #KinoGer Suche
            #http://kinoger.com/index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&story=bright
            #print "print local title", localtitle
            # first iteration of session object to be parsed for search
            url="http://kinoger.com/index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&titleonly=3&sortby=title&resorder=asc&story="+ str(localtitle)+" "+str(year)
            print "print search url", url
            #self.search anstelle url

                       
            
            sHtmlContent=self.scraper.get(url).content
            #print "print Kinoger Content", sHtmlContent
            # suche nach <span class="buttons"><a href="http://kinoger.com/stream/5378-paddington-2-2017.html"><span><b>Play</b></span></a></span>
            
            pattern = '<span class="buttons"><a href="([^"]+).*?'
            aResult = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
            #print "print search a Result", type(aResult),aResult
            url=re.sub(r'<span class="buttons"><a href="','',aResult[1])
            

#NEED FIX!! teste ob titel in Resutl, da suchergebnisauch an 2te stel sein kann !!
            
            print "print search return url",url
            #<img src="/templates/kinoger/images/ico/postinfo-icon.png" alt="" class="img" /> <a href="http://kinoger.com/stream/5375-bright-2017.html">Bright (2017) Film</a>
            #url = "http://kinoger.com/stream/5011-dunkirk-2017.html" #"http://kinoger.com/stream/5375-bright-2017.html"      http://kinoger.com/stream/5266-happy-death-day-2017.html                     
                
            return url
        except:
            return
