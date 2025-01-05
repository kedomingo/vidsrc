import json
import math
import sys
from urllib.parse import parse_qs
from urllib.parse import quote
from urllib.parse import urlencode
from ext.extensions import MyPlayer
from ext.extensions import PlaybackMonitor
import requests
import xbmc
import xbmcgui
import xbmcplugin

BASE_URL = "https://api.themoviedb.org/3"
THUMB_BASE_URL = "https://image.tmdb.org/t/p/w185"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
API_KEY = "d75677fb857aa6f339c67d9ba89f9aed"  # DO NOT COMMIT

ADDON_HANDLE = int(sys.argv[1])
SERVER_ADDRESS = 'http://firestreamarr.xyz:8080'


def log(message, level=xbmc.LOGINFO):
  xbmc.log(message, level)


def __show_notification(title, message):
  # Create a dialog box with a title and message
  xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, 5000)


def __build_url(query, base=None):
  base = base if base else sys.argv[0]
  prepared_query = {}
  for k, v in query.items():
    if isinstance(v, dict):
      prepared_query[k] = json.dumps(v)
    else:
      prepared_query[k] = v
  return f"{base}?{urlencode(prepared_query)}"


def __tmdb_api_get(url):
  response = requests.get(url)
  response.raise_for_status()
  return response.json()


def main_menu():
  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url(
          {'action': 'submenu', 'type': 'movie', 'content': 'tvshows'}),
      xbmcgui.ListItem('Movies'),
      isFolder=True)

  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url({'action': 'submenu', 'type': 'tv', 'content': 'tvshows'}),
      xbmcgui.ListItem('TV'),
      isFolder=True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def submenu(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])

  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url(__append_dicts(params, {'action': 'trending'})),
      xbmcgui.ListItem(f'Trending {typelabel}'),
      isFolder=True)

  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url(__append_dicts(params, {'action': 'genres'})),
      xbmcgui.ListItem(f'{typelabel} By Genre'),
      isFolder=True)

  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url(__append_dicts(params, {'action': 'periods'})),
      xbmcgui.ListItem(f'{typelabel} By Period'),
      isFolder=True)

  xbmcplugin.addDirectoryItem(
      ADDON_HANDLE,
      __build_url(__append_dicts(params, {'action': 'find'})),
      xbmcgui.ListItem(f'Find {typelabel}'),
      isFolder=True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_trending(params):
  if 'page' not in params:
    params['page'] = 1
  if 'type' not in params:
    params['type'] = 'movie'

  page = params['page']
  type = params['type']
  url = f"{BASE_URL}/trending/{type}/day?api_key={API_KEY}&page={page}"
  log(f'URL {url}')
  data = __tmdb_api_get(url)

  __previous_pages(page, params)

  for show in data['results']:
    __list_show(show, params['type'], params['content'])

  __next_pages(page, data['total_pages'], params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_genres(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'type' not in params:
    params['type'] = 'movie'

  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  url = f"{BASE_URL}/genre/{params['type']}/list?api_key={API_KEY}"
  data = __tmdb_api_get(url)

  for genre in data['genres']:
    args = {'action': 'discover', 'genre_id': genre['id'],
            'genre_name': genre['name']}
    url = __build_url(__append_dicts(params, args))
    list_item = xbmcgui.ListItem(f"{genre['name']} {typelabel}")
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  args = {'action': 'discover', 'genre_all': 'genre_all'}
  url = __build_url(__append_dicts(params, args))
  list_item = xbmcgui.ListItem('ALL')
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_periods(params):
  if params['type'] == 'tv':
    typelabel = 'TV Shows'
  else:
    typelabel = 'Movies'

  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  periods = {
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
    'ALL': {'date_all': 'date_all'},
  }

  for period, bounds in periods.items():
    args = {'action': 'discover'}
    bounds.update(params)
    bounds.update(args)
    url = __build_url(bounds)
    label = f'{typelabel} from all periods' if period == 'ALL' else f'{typelabel} from {period}'
    list_item = xbmcgui.ListItem(label)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def discover(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  page = params['page'] if 'page' in params else 1

  if 'type' not in params:
    params['type'] = 'movie'

  if 'genre_id' not in params and 'genre_all' not in params:
    list_genres(params)
    return

  if 'date_gte' not in params and 'date_lte' not in params and 'date_all' not in params:
    list_periods(params)
    return

  request = {'api_key': API_KEY}

  if 'genre_all' not in params:
    if 'genre_id' in params:
      request['with_genres'] = params['genre_id']

  if 'date_all' not in params:
    if 'date_gte' in params:
      request['primary_release_date.gte'] = params['date_gte']
    if 'date_lte' in params:
      request['primary_release_date.lte'] = params['date_lte']

  request['sort_by'] = 'popularity.desc'

  url = __build_url(
      __append_dicts({'page': page}, request),
      f"{BASE_URL}/discover/{params['type']}"
  )
  log(f"Discover URL {url}")

  data = __tmdb_api_get(url)

  __previous_pages(page, params)

  for show in data['results']:
    __list_show(show, params['type'], params['content'])

  __next_pages(page, data['total_pages'], params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def find_movies(params):
  keyboard = xbmc.Keyboard('', 'Enter search term')
  keyboard.doModal()
  if keyboard.isConfirmed():
    params['query'] = keyboard.getText()

    search_movies(params)


def search_movies(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'type' not in params:
    params['type'] = 'movie'

  page = params['page'] if 'page' in params else 1
  query = params['query']

  url = f"{BASE_URL}/search/{params['type']}?api_key={API_KEY}&query={quote(query)}&page={page}"
  data = __tmdb_api_get(url)

  __previous_pages(page, params)

  for show in data['results']:
    __list_show(show, params['type'], params['content'])

  __next_pages(page, data['total_pages'], params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def select_tv(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'page' not in params:
    params['page'] = 1
  if 'type' not in params:
    params['type'] = 'tv'

  page = params['page']
  type = params['type']
  url = f"{BASE_URL}/{type}/{params['tmdb_id']}?api_key={API_KEY}&page={page}"
  log(f'URL {url}')
  data = __tmdb_api_get(url)

  # if data['number_of_seasons'] == 1:
  #   select_season(params)

  for season in data['seasons']:
    season['backdrop_path'] = data['backdrop_path']
    season['first_air_date'] = season['air_date']
    season['vote_count'] = data['vote_count']
    season['popularity'] = data['popularity']
    # use the show id to identify this
    season['id'] = data['id']
    __list_show(season, 'tv_season', params['content'])

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def select_tv_season(params):
  xbmcplugin.setContent(handle=ADDON_HANDLE, content=params['content'])
  if 'page' not in params:
    params['page'] = 1
  if 'type' not in params:
    params['type'] = 'tv'

  page = params['page']
  type = params['type']
  url = f"{BASE_URL}/{type}/{params['tmdb_id']}/season/{params['season_number']}?api_key={API_KEY}&page={page}"
  log(f'URL {url}')
  data = __tmdb_api_get(url)

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
    __list_show(episode, 'movie', params['content'])

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
    url = __build_url(
        __append_dicts(params, {'action': 'play_movie', 'resolver': streamer}))
    list_item = xbmcgui.ListItem(label)

    list_item.setArt(art)
    list_item.setInfo(type="video", infoLabels=infoLabels)
    list_item.setProperty("IsPlayable", 'True')

    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, isFolder=False)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play_movie(params, tries=0):
  tmdb_id = params['tmdb_id']
  resolver = params['resolver'] if 'resolver' in params else None
  log(f"Resolving {tmdb_id}")

  playback_url = None
  subtitles = None
  error_message = None

  message = f'{tries + 1}: Resolving {tmdb_id}'

  if 'episode_number' in params:
    request_params = {
      'episode_number': params['episode_number'],
      'season_number': params['season_number'],
      'tv_id': tmdb_id,
    }
    message += f" ep. {params['episode_number']}"
  else:
    request_params = {'movieid': tmdb_id,}

  if resolver:
    request_params['resolver'] = resolver
    message += f' via {resolver}'

  if tries > 0:
    request_params['nocache'] = 1

  try:
    __show_notification('Info', message)

    server_url = __build_url(request_params, f'{SERVER_ADDRESS}/fetch')
    log(f'Server URL {server_url}')
    result = requests.get(server_url)
    data = json.loads(result.text)
    log(f"Got response {result.text}")
    error_message = data['error'] if 'error' in data else None

    if not error_message:
      __show_notification('Success', 'rendering')
      playback_url = data['playlist'] if 'playlist' in data else None
      log(f"Got playback url {playback_url}")
      subtitles = data['subtitles'] if 'subtitles' in data else None
  except Exception as e:
    error_message = f"- {e}"

  if playback_url is None:
    __show_notification("Error",
                        f"Could not resolve movie {tmdb_id} {error_message}")
    log(f"Could not resolve movie {tmdb_id}")
    return

  log(f"Playing vidsrc {playback_url}")

  # Create a ListItem for playback
  list_item = xbmcgui.ListItem(path=playback_url)
  xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=True,
                            listitem=list_item)

  player = MyPlayer()
  player.play(playback_url, list_item)
  monitor = PlaybackMonitor()

  set_subtitles(subtitles, player)
  # Retry once on failure
  if tries == 0:
    handle_retry_on_failure(tries, player, monitor)


def set_subtitles(subtitles, player: xbmc.Player):
  if subtitles:
    while not player.isPlaying():
      xbmc.sleep(100)

    if len(subtitles) == 1:
      engsub = str(subtitles[0])
      if engsub.startswith('/'):
        engsub = f'{SERVER_ADDRESS}{engsub}'
      log(f"Found engsub {engsub}")
      player.setSubtitles(engsub)
      return

    # no choice - display all - add in reverse order
    log(f"Adding all {len(subtitles)} subs")
    for subtitle_url in subtitles[::-1]:
      player.setSubtitles(subtitle_url)


def handle_retry_on_failure(tries, player: xbmc.Player, monitor: xbmc.Monitor):
  while not monitor.abortRequested():
    if monitor.waitForAbort(1):
      break
    if player.isPlaying():
      log("Item is playing!")
      break

  if player.playback_failed or monitor.playback_failed:
    play_movie(movie_id, tries=tries + 1)


def __list_show(show, type, content_type='movies'):
  name = show['title'] if 'title' in show else show['name']
  release_year = show['release_date'][:4] \
    if 'release_date' in show and show['release_date'] else None
  if not release_year:
    release_year = show['first_air_date'][:4] \
      if 'first_air_date' in show and show['first_air_date'] else None

  title = f"{name} ({release_year if release_year else 'N/A'})"
  rating = f"{round(show['vote_average'], 2)} ({show['vote_count']})"
  normalized_rating = __normalize_score(
      show['popularity'],
      show['vote_count'],
      show['vote_average']
  )
  plot = f"{show['overview']}\n\nRating: {rating}\nNormalized Rating: {normalized_rating}"
  backdrop = show['backdrop_path'] if 'backdrop_path' in show and show[
    'backdrop_path'] else ''
  poster = show['poster_path'] if 'poster_path' in show and show[
    'poster_path'] else ''

  art = {
    'poster': IMAGE_BASE_URL + (poster if poster else backdrop),
    'fanart': IMAGE_BASE_URL + (backdrop if backdrop else poster),
    'banner': IMAGE_BASE_URL + (backdrop if backdrop else poster),
    'thumb': IMAGE_BASE_URL + (poster if poster else backdrop),
    'icon': IMAGE_BASE_URL + (poster if poster else backdrop)
  }
  infoLabels = {
    'title': title,
    'plot': plot,
    'Rating': str(normalized_rating)
  }
  list_item = xbmcgui.ListItem(title)
  list_item.setArt(art)
  list_item.setInfo(type="video", infoLabels=infoLabels)
  list_item.setProperty("IsPlayable", 'False')
  action = f'select_{type}'
  urlparams = {
    'content': content_type,
    'action': action,
    'tmdb_id': show['id'],
    'art': art,
    'infoLabels': infoLabels
  }
  if 'season_number' in show:
    urlparams['season_number'] = show['season_number']
  if 'episode_number' in show:
    urlparams['episode_number'] = show['episode_number']
  url = __build_url(urlparams)
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, isFolder=True)


def __normalize_score(popularity, reviews, review_score):
  if reviews <= 22:
    review_factor = 0.55 + (0.0005 * reviews * reviews)
  else:
    # math.log is base e by default. but we want to be explicit
    review_factor = 0.3 * math.log(reviews - 9, math.e)
  review_factor = min(review_factor, 1.2)

  # popularity does not affect score if low enough, reviews will affect solely
  if popularity <= 300:
    popularity_factor = 1
    review_factor = min(1, review_factor)
  else:
    popularity_factor = min(1, (popularity + 100) / (450 * review_factor))

  review_factor = min(1.07, review_factor)

  # Final score calculation
  return round(
      max(0, min(review_score * review_factor * popularity_factor, 10)), 2)


def on_action(action, control_id):
  log(f"ListItem Action: {action}")


def __previous_pages(page, params):
  page = int(page)
  if page > 1:
    main_url = __build_url({})
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, main_url,
                                xbmcgui.ListItem('Back to main page'), True)

    prev_url = __build_url(__append_dicts(params, {'page': 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem('First'), True)

  if page > 10:
    prev_url = __build_url(__append_dicts(params, {'page': page - 10}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 10}'), True)

  if page > 2:
    prev_url = __build_url(__append_dicts(params, {'page': page - 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 1}'), True)


def __next_pages(page, total_pages, params):
  page = int(page)
  if page < total_pages:
    next_url = __build_url(__append_dicts(params, {'page': page + 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 1}'), True)

  if page + 2 < total_pages:
    next_url = __build_url(__append_dicts(params, {'page': page + 2}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 2}'), True)

  if page + 5 < total_pages:
    next_url = __build_url(__append_dicts(params, {'page': page + 5}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 5}'), True)

  if page + 1 < total_pages:
    next_url = __build_url(__append_dicts(params, {'page': total_pages - 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem('Last'), True)


def __append_dicts(dict1, dict2):
  dict1.update(dict2)
  return dict1


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
