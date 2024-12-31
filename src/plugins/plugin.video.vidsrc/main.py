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
SERVER_ADDRESS = 'http://192.168.0.145:8080'


def show_notification(title, message):
  # Create a dialog box with a title and message
  xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, 5000)


def build_url(query, base=None):
  base = base if base else sys.argv[0]
  return f"{base}?{urlencode(query)}"


def get_json(url):
  response = requests.get(url)
  response.raise_for_status()
  return response.json()


def main_menu():
  xbmcplugin.setContent(handle=ADDON_HANDLE, content='videos')

  # Add Trending option
  url = build_url({'action': 'trending', 'page': 1})
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url,
                              xbmcgui.ListItem('Trending Movies'),
                              True)

  # Add Genre option
  url = build_url({'action': 'genres'})
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('By Genre'),
                              True)

  # Add Periods option
  url = build_url({'action': 'periods'})
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('By Period'),
                              True)

  # Add Find option
  url = build_url({'action': 'find'})
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('Find'), True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_trending(page):
  url = f"{BASE_URL}/trending/movie/day?api_key={API_KEY}&page={page}"
  data = get_json(url)

  __previous_pages(page, {'action': 'trending'})

  for movie in data['results']:
    __list_movie(movie)

  __next_pages(page, data['total_pages'], {'action': 'trending'})

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_genres(params=None):
  url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}"
  data = get_json(url)

  for genre in data['genres']:
    args = {'action': 'discover', 'genre_id': genre['id'],
            'genre_name': genre['name']}
    url = build_url(__append_dicts(params, args))
    list_item = xbmcgui.ListItem(genre['name'])
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  args = {'action': 'discover', 'genre_all': 'genre_all'}
  url = build_url(__append_dicts(params, args))
  list_item = xbmcgui.ListItem('ALL')
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_periods(params):
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
    url = build_url(bounds)
    list_item = xbmcgui.ListItem(period)
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def discover(params, page):
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

  url = build_url(__append_dicts({'page': page}, request),
                  f"{BASE_URL}/discover/movie")
  xbmc.log(f"Discover URL {url}", level=xbmc.LOGINFO)

  data = get_json(url)

  __previous_pages(page, params)

  for movie in data['results']:
    __list_movie(movie)

  __next_pages(page, data['total_pages'], params)

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def find_movies():
  keyboard = xbmc.Keyboard('', 'Enter search term')
  keyboard.doModal()
  if keyboard.isConfirmed():
    query = keyboard.getText()
    page = 1
    search_movies(query, page)


def search_movies(query, page):
  url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={quote(query)}&page={page}"
  data = get_json(url)

  __previous_pages(page, {'action': 'search', 'query': query})

  for movie in data['results']:
    __list_movie(movie)

  __next_pages(page, data['total_pages'], {'action': 'search', 'query': query})

  xbmcplugin.endOfDirectory(ADDON_HANDLE)


def play_movie(tmdb_id, tries=0):
  xbmc.log(f"Resolving {tmdb_id}", level=xbmc.LOGINFO)

  playback_url = None
  subtitles = None
  error_message = None
  try:
    server_url = f"{SERVER_ADDRESS}/fetch?movieid={tmdb_id}"
    if tries > 0:
      server_url += '&nocache=1'

    result = requests.get(server_url)
    data = json.loads(result.text)
    xbmc.log(f"Got response {result.text}", level=xbmc.LOGINFO)
    error_message = data['error'] if 'error' in data else None

    if not error_message:
      playback_url = data['playlist'] if 'playlist' in data else None
      xbmc.log(f"Got playback url {playback_url}", level=xbmc.LOGINFO)
      subtitles = data['subtitles'] if 'subtitles' in data else None
  except Exception as e:
    error_message = f"- {e}"

  if playback_url is None:
    show_notification("Error",
                      f"Could not resolve movie {tmdb_id} {error_message}")
    xbmc.log(f"Could not resolve movie {tmdb_id}", level=xbmc.LOGINFO)
    return

  xbmc.log(f"Playing vidsrc {playback_url}", level=xbmc.LOGINFO)

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
        engsub = f'http://192.168.0.145:8080{engsub}'
      xbmc.log(f"Found engsub {engsub}", level=xbmc.LOGINFO)
      player.setSubtitles(engsub)
      return

    # no choice - display all
    xbmc.log(f"Adding all {len(subtitles)} subs", level=xbmc.LOGINFO)
    for subtitle_url in subtitles:
      player.setSubtitles(subtitle_url)


def handle_retry_on_failure(tries, player: xbmc.Player, monitor: xbmc.Monitor):
  while not monitor.abortRequested():
    if monitor.waitForAbort(1):
      break
    if player.isPlaying():
      xbmc.log("Item is playing!", xbmc.LOGINFO)
      break

  if player.playback_failed or monitor.playback_failed:
    play_movie(movie_id, tries=tries + 1)


def __list_movie(movie):
  title = f"{movie['title']} ({movie['release_date'][:4] if 'release_date' in movie and movie['release_date'] else 'N/A'})"
  rating = f"{round(movie['vote_average'], 2)} ({movie['vote_count']})"
  normalized_rating = __normalize_score(movie['popularity'], 1500,
                                        movie['vote_count'],
                                        movie['vote_average'])
  plot = f"{movie['overview']}\n\nRating: {rating}\nNormalized Rating: {normalized_rating}"
  backdrop = movie['backdrop_path'] if 'backdrop_path' in movie and movie[
    'backdrop_path'] else ''
  poster = movie['poster_path'] if 'poster_path' in movie and movie[
    'poster_path'] else ''

  list_item = xbmcgui.ListItem(title)
  list_item.setArt(
      {
        'poster': IMAGE_BASE_URL + (poster if poster else backdrop),
        'banner': IMAGE_BASE_URL + (backdrop if backdrop else poster),
        'thumb': THUMB_BASE_URL + (poster if poster else backdrop),
        'icon': THUMB_BASE_URL + (poster if poster else backdrop)
      }
  )
  list_item.setInfo(type="video", infoLabels={
    'title': title,
    'plot': plot,
    'Rating': str(normalized_rating)
  })
  list_item.setProperty("IsPlayable", 'True')
  url = build_url({'action': 'play_movie', 'id': movie['id']})
  xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, False)


def __normalize_score(popularity, max_popularity, reviews, review_score):
  # bound to 0-10
  # return round(max(0, min(review_score * pop_factor * review_factor, 10)), 2)
  max_reviews = 400
  review_factor = min(1, math.log(reviews + 105) / math.log(max_reviews + 1))

  print(review_factor)
  # popularity does not affect a highly reviewed show
  popularity_factor = 1
  if review_factor < 0.8:
    popularity_factor = math.log(popularity + 1) / math.log(max_popularity + 1)

  # Final score calculation
  return round(
      max(0, min(review_score * review_factor * popularity_factor, 10)), 2)


def on_action(action, control_id):
  xbmc.log(f"ListItem Action: {action}", level=xbmc.LOGINFO)


def __previous_pages(page, params):
  if page > 1:
    main_url = build_url({})
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, main_url,
                                xbmcgui.ListItem('Back to main page'), True)

    prev_url = build_url(__append_dicts(params, {'page': 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem('First'), True)

  if page > 10:
    prev_url = build_url(__append_dicts(params, {'page': page - 10}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 10}'), True)

  if page > 2:
    prev_url = build_url(__append_dicts(params, {'page': page - 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url,
                                xbmcgui.ListItem(f'Page {page - 1}'), True)


def __next_pages(page, total_pages, params):
  if page < total_pages:
    next_url = build_url(__append_dicts(params, {'page': page + 1}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 1}'), True)

  if page + 2 < total_pages:
    next_url = build_url(__append_dicts(params, {'page': page + 2}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 2}'), True)

  if page + 5 < total_pages:
    next_url = build_url(__append_dicts(params, {'page': page + 5}))
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url,
                                xbmcgui.ListItem(f'Page {page + 5}'), True)

  if page + 1 < total_pages:
    next_url = build_url(__append_dicts(params, {'page': total_pages - 1}))
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

# xbmc.log(f"Action: {action}", level=xbmc.LOGINFO)
# xbmc.log(f"Params: {request_params}", level=xbmc.LOGINFO)

if action is None:
  main_menu()
elif action == 'trending':
  list_trending(page)
elif action == 'genres':
  list_genres(request_params)
elif action == 'periods':
  list_periods(request_params)
elif action == 'discover':
  discover(request_params, page)
elif action == 'find':
  find_movies()
elif action == 'search':
  query = params['query'][0]
  search_movies(query, page)
elif action == 'play_movie':
  movie_id = params['id'][0]
  xbmc.log(f"Movie ID: {movie_id}", level=xbmc.LOGINFO)
  play_movie(movie_id)
