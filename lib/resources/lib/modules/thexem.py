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

import json
from resources.lib.modules import client

URL_PATTERN = 'http://thexem.de/map/single?id=%s&origin=tvdb&season=%s&episode=%s&destination=scene'

def get_scene_episode_number(tvdbid, season, episode):

    try:
        url = URL_PATTERN % (tvdbid, season, episode)
        r = client.request(url)
        r = json.loads(r)
        if r['result'] == 'success':
            data = r['data']['scene']
            return data['season'], data['episode']            
    except:
        pass

    return season, episode    
