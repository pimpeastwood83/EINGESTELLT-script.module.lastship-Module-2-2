# -*- coding: UTF-8 -*-

"""
    Lastship Add-on (C) 2017
    Credits to Placenta and Covenant; our thanks go to their creators

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

# Addon Name: lastship
# Addon id: plugin.video.lastship
# Addon Provider: LastShip

import xbmc
import requests
import json
import time

class tmdbMetacatcher:
    def __init__(self):
        self.base_link = 'http://api.themoviedb.org'
        self.search_link = 'http://api.themoviedb.org/3/search/movie?api_key=%s&language=de-DE&page=1&include_adult=false&query=%s'
        self.detail_link = 'http://api.themoviedb.org/3/movie/%d?api_key=%s&language=de-DE&append_to_response=images'
        self.api_request_limit = 4
        self.session = requests.Session()
        self.meta_keychange = {'imdb_id':'imdb',
                               'original_title':'originaltitle',
                               'overview':'plot',
                               'runtime':'duration',
                               'vote_average':'rating',
                               'vote_count':'votes',
                               'title' : 'title'}

    def getMetaFromIDs(self, id_list, user):
        xbmc.log("Requesting Meta from TMDB for list with %d entries" % len(id_list))
        metaList = []
        for id in id_list:
            nextId = False
            while nextId is False and self.api_request_limit > 0:
                try:
                    meta = self.getMetaFromID(id,user)
                    if "status_code" in meta and meta["status_code"] is 25: #too many requests, lets wait a sec.
                        xbmc.log("TMDB limit reached. Wait 5 seconds...")
                        time.sleep(5)
                        continue
                    meta = dict((self.meta_keychange[key], value) for (key, value) in meta.items() if key in self.meta_keychange)
                    metaList.append(meta)
                    nextId = True
                except Exception as e:
                    xbmc.log("Exception in TMDB while getMeta for id %d" %id)
                    xbmc.log(e.message)
                    self.api_request_limit = self.api_request_limit - 1
        return metaList



    def getMetaFromID(self, id, user):
        xbmc.log("Requesting Meta from TMDB for id %d" % id)
        r = self.session.get(self.detail_link % (id,user))
        res = r.json()
        xbmc.log("Meta from TMDB for id %d: %s" % (id, json.dumps(res)))
        return res
