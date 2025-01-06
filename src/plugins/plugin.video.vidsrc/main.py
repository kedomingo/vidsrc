import hashlib
import json
import sys
from urllib.parse import parse_qs

import xbmc
import xbmcgui
import xbmcplugin

from client.firestreamarr_client import FirestreamarrClient
from client.tmdb_client import TmdbClient
from resolver.player import Player
from util.lister import Lister
from util.pagination import previous_pages, next_pages
from util.util import log, append_dicts, build_url
from util.cache import cache_get

ADDON_HANDLE = int(sys.argv[1])
ADDON_BASE_URL = sys.argv[0]

API_KEY = "d75677fb857aa6f339c67d9ba89f9aed"  # DO NOT COMMIT

client = TmdbClient(API_KEY)
fs_client = FirestreamarrClient()

li = Lister(ADDON_HANDLE, ADDON_BASE_URL)


def main_menu():
  li.add_items({
    'Movies': {'action': 'submenu', 'type': 'movie', 'content': 'tvshows'},
    'TV': {'action': 'submenu', 'type': 'tv', 'content': 'tvshows'}
  })


def submenu(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])

  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  li.add_items({
    f'Trending {typelabel}': append_dicts(params, {'action': 'trending'}),
    f'{typelabel} By Genre': append_dicts(params, {'action': 'genres'}),
    f'{typelabel} By Period': append_dicts(params, {'action': 'periods'}),
    f'Find {typelabel}': append_dicts(params, {'action': 'find'}),
  })


def list_genres(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'type' not in params:
    params['type'] = 'movie'

  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  data = client.list_genres(params['type'])

  items = {}
  items['All genres'] = append_dicts(
      params,
      {
        'action': 'discover',
        'genre_all': 'genre_all',
      }
  )
  for genre in data['genres']:
    items[f"{genre['name']} {typelabel}"] = append_dicts(
        params,
        {
          'action': 'discover',
          'genre_id': genre['id'],
          'genre_name': genre['name']
        }
    )

  li.add_items(items)


def list_periods(params):
  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  periods = {
    'ALL': {'date_all': 'date_all'},
    '2025': {'date_gte': '2025-01-01', 'date_lte': '2025-12-31'},
    '2024': {'date_gte': '2024-01-01', 'date_lte': '2024-12-31'},
    '2023': {'date_gte': '2023-01-01', 'date_lte': '2023-12-31'},
    '2022': {'date_gte': '2022-01-01', 'date_lte': '2022-12-31'},
    '2021': {'date_gte': '2021-01-01', 'date_lte': '2021-12-31'},
    '2020': {'date_gte': '2020-01-01', 'date_lte': '2020-12-31'},
    '2020s': {'date_gte': '2020-01-01'},
    '2010s': {'date_gte': '2010-01-01', 'date_lte': '2019-12-31'},
    '2000s': {'date_gte': '2000-01-01', 'date_lte': '2009-12-31'},
    '1990s': {'date_gte': '1990-01-01', 'date_lte': '1999-12-31'},
    '1980s': {'date_gte': '1980-01-01', 'date_lte': '1989-12-31'},
    '1970s': {'date_gte': '1970-01-01', 'date_lte': '1979-12-31'},
    'pre-1970s': {'date_lte': '1969-12-31'},
  }

  items = {}
  for period, bounds in periods.items():
    label = f'{typelabel} from all periods' if period == 'ALL' else f'{typelabel} from {period}'
    items[label] = append_dicts(
        params, append_dicts({'action': 'discover'}, bounds)
    )

  li.add_items(items)


def list_trending(params):
  if 'page' not in params:
    params['page'] = 1
  if 'type' not in params:
    params['type'] = 'movie'

  data = client.trending(params['type'], params['page'])

  previous_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], params)

  for show in data['results']:
    li.list_show(show, params['type'], params['content'])

  next_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], data['total_pages'],
             params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def discover(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])

  log(params)
  if 'page' not in params:
    params['page'] = 1

  if 'type' not in params:
    params['type'] = 'movie'

  if 'genre_id' not in params and 'genre_all' not in params:
    list_genres(params)
    return

  if 'date_gte' not in params and 'date_lte' not in params and 'date_all' not in params:
    list_periods(params)
    return

  data = client.discover(params['type'], params, params['page'])

  previous_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], params)

  for show in data['results']:
    li.list_show(show, params['type'], params['content'])

  next_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], data['total_pages'],
             params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def find_movies(params):
  keyboard = xbmc.Keyboard('', 'Enter search term')
  keyboard.doModal()
  if keyboard.isConfirmed():
    params['query'] = keyboard.getText()

    search_movies(params)


def search_movies(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])

  if 'page' not in params:
    params['page'] = 1

  if 'type' not in params:
    params['type'] = 'movie'

  data = client.search(params['type'], params['query'], params['page'])

  previous_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], params)

  for show in data['results']:
    li.list_show(show, params['type'], params['content'])

  next_pages(ADDON_HANDLE, ADDON_BASE_URL, params['page'], data['total_pages'],
             params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def select_tv(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'type' not in params:
    params['type'] = 'tv'

  data = client.show_details(params['type'], params['tmdb_id'])

  # TODO
  # if data['number_of_seasons'] == 1:
  #   select_season(params)

  for season in data['seasons']:
    season['backdrop_path'] = data['backdrop_path']
    season['first_air_date'] = season['air_date']
    season['vote_count'] = data['vote_count']
    season['popularity'] = data['popularity']
    # use the show id to identify this
    season['id'] = data['id']
    li.list_show(season, 'tv_season', params['content'])

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def select_tv_season(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])

  if 'type' not in params:
    params['type'] = 'tv'

  data = client.season_details(params['tmdb_id'], params['season_number'])

  for episode in data['episodes']:
    episode['name'] = f"{episode['episode_number']}. {episode['name']}"
    episode['poster_path'] = episode['still_path']
    episode['backdrop_path'] = episode['still_path']
    episode['first_air_date'] = episode['air_date']
    # no data. set high enough to have 1 popularity factor in normalization
    episode['popularity'] = 3000
    # use the show id to identify this
    episode['id'] = params['tmdb_id']

    # movie = Playable
    li.list_show(episode, 'movie', params['content'])

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def select_movie(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  window = xbmcgui.Window(10000)
  window.setProperty('title', 'Select stream provider')
  streamers = {
    'vidsrc - movie, tv': 'vidsrc',
    'autoembed - movie, tv': 'autoembed',
    'vidlink - movie': 'vidlink',
    'vidsrcicu - movie': 'vidsrcicu',
    'cineby - movie': 'cineby',  # redirecting to about:blank frequently
  }
  art = json.loads(params['art'])
  infoLabels = json.loads(params['infoLabels'])
  for label, streamer in streamers.items():
    url = build_url(
        append_dicts(params, {'action': 'play_movie', 'resolver': streamer}),
        ADDON_BASE_URL
    )
    list_item = xbmcgui.ListItem(label)

    list_item.setArt(art)
    list_item.setInfo(type="video", infoLabels=infoLabels)
    list_item.setProperty("IsPlayable", 'True')

    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, isFolder=False)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play_movie(params):
  if 'episode_number' in params:
    media_id = f"{params['tmdb_id']}.{params['season_number']}.{params['episode_number']}"
    params['type'] = 'tv'
  else:
    media_id = params['tmdb_id']
    params['type'] = 'movie'

  last_position_cache_key = f"{params['type']}-{media_id}-{params['resolver']}"
  last_position_seconds = cache_get(
      last_position_cache_key,
      'last-position',
      not_older_than_days=30
  )

  player = None
  if last_position_seconds:
    dialog = xbmcgui.Dialog()
    result = dialog.yesno(
        'Resume playback?',
        f'Do you want to resume playback from {__format_time(last_position_seconds)}?'
    )

    if result == 1:
      log('User clicked Yes')
      player = Player(
          ADDON_HANDLE,
          ADDON_BASE_URL,
          fs_client,
          play_from_seconds=last_position_seconds
      )

  if player is None:
    player = Player(ADDON_HANDLE, ADDON_BASE_URL, fs_client)

  player.play_movie(params)


def __format_time(seconds):
  minutes, seconds = divmod(seconds, 60)
  hours, minutes = divmod(minutes, 60)

  if hours > 0:
    return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
  else:
    return f"{int(minutes):02}:{int(seconds):02}"


## -----------------------------------

params = parse_qs(sys.argv[2][1:])
action = params.get('action', [None])[0]
page = int(params.get('page', [1])[0])

request_params = {}
for k, v in params.items():
  request_params[k] = v[0]

log(f"Action: {action}")
# log(f"Params: {request_params}")

if action is None:
  main_menu()
elif action == 'submenu':
  submenu(request_params)
elif action == 'trending':
  list_trending(request_params)
elif action == 'genres':
  list_genres(request_params)
elif action == 'periods':
  list_periods(request_params)
elif action == 'discover':
  discover(request_params)
elif action == 'find':
  find_movies(request_params)
elif action == 'search':
  search_movies(request_params)
elif action == 'select_movie':
  select_movie(request_params)
elif action == 'select_tv':
  select_tv(request_params)
elif action == 'select_tv_season':
  select_tv_season(request_params)
elif action == 'play_movie':
  play_movie(request_params)
