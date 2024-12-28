import sys
import xbmc
import xbmcgui
import xbmcplugin
import requests
from urllib.parse import parse_qs
from urllib.parse import urlencode
from urllib.parse import quote
from resolver import vidsrc

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w185"
API_KEY = ""

ADDON_HANDLE = int(sys.argv[1])

def build_url(query):
    return f"{sys.argv[0]}?{urlencode(query)}"


def get_json(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()


def main_menu():
    xbmcplugin.setContent(handle=ADDON_HANDLE, content='videos')

    # Add Trending option
    url = build_url({'action': 'trending', 'page': 1})
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('Trending'), True)

    # Add Genre option
    url = build_url({'action': 'genres'})
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('Genre'), True)

    # Add Find option
    url = build_url({'action': 'find'})
    xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, xbmcgui.ListItem('Find'), True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_trending(page):
    url = f"{BASE_URL}/trending/movie/day?api_key={API_KEY}&page={page}"
    data = get_json(url)

    if page > 1:
        main_url = build_url({})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, main_url,
                                    xbmcgui.ListItem('Back to main page'), True)

        prev_url = build_url({'action': 'trending', 'page': page - 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url, xbmcgui.ListItem('Previous page'), True)

    for movie in data['results']:
        title = f"{movie['title']} ({movie['release_date'][:4] if 'release_date' in movie and movie['release_date'] else 'N/A'})"
        list_item = xbmcgui.ListItem(title)
        list_item.setArt({'poster': IMAGE_BASE_URL + movie['poster_path'] if 'poster_path' in movie and movie['poster_path'] else ''})
        url = build_url({'action': 'play_movie', 'id': movie['id']})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, False)

    if page < data['total_pages']:
        next_url = build_url({'action': 'trending', 'page': page + 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url, xbmcgui.ListItem('Next page'), True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_genres():
    url = f"{BASE_URL}/genre/movie/list?api_key={API_KEY}"
    data = get_json(url)

    for genre in data['genres']:
        url = build_url({'action': 'movies_by_genre', 'genre_id': genre['id'], 'genre_name': genre['name'], 'page': 1})
        list_item = xbmcgui.ListItem(genre['name'])
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)


def list_movies_by_genre(genre_id, genre_name, page):
    url = f"{BASE_URL}/discover/movie?api_key={API_KEY}&with_genres={genre_id}&page={page}"
    data = get_json(url)

    if page > 1:
        main_url = build_url({})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, main_url,
                                    xbmcgui.ListItem('Back to main page'), True)

        prev_url = build_url({'action': 'movies_by_genre', 'genre_id': genre_id, 'genre_name': genre_name, 'page': page - 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url, xbmcgui.ListItem('Previous page'), True)

    for movie in data['results']:
        title = f"{movie['title']} ({movie['release_date'][:4] if 'release_date' in movie and movie['release_date'] else 'N/A'})"
        list_item = xbmcgui.ListItem(title)
        list_item.setArt({'poster': IMAGE_BASE_URL + movie['poster_path'] if 'poster_path' in movie and movie['poster_path'] else ''})
        url = build_url({'action': 'play_movie', 'id': movie['id']})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, False)

    if page < data['total_pages']:
        next_url = build_url({'action': 'movies_by_genre', 'genre_id': genre_id, 'genre_name': genre_name, 'page': page + 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url, xbmcgui.ListItem('Next page'), True)

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

    if page > 1:
        prev_url = build_url({'action': 'search', 'query': query, 'page': page - 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, prev_url, xbmcgui.ListItem('Previous page'), True)

    for movie in data['results']:
        title = f"{movie['title']} ({movie['release_date'][:4] if 'release_date' in movie and movie['release_date'] else 'N/A'})"
        list_item = xbmcgui.ListItem(title)
        list_item.setArt({'poster': IMAGE_BASE_URL + movie['poster_path'] if 'poster_path' in movie and movie['poster_path'] else ''})
        url = build_url({'action': 'play_movie', 'id': movie['id']})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url, list_item, False)

    if page < data['total_pages']:
        next_url = build_url({'action': 'search', 'query': query, 'page': page + 1})
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, next_url, xbmcgui.ListItem('Next page'), True)

    xbmcplugin.endOfDirectory(ADDON_HANDLE)

def play_movie(movie_id):

    xbmc.log(f"Resolving {movie_id}", level=xbmc.LOGINFO)

    # Derive the actual URL (replace this with your logic)
    playback_url = vidsrc.resolve(movie_id)
    if playback_url is None:
        xbmc.log(f"Could not resolve movie {movie_id}", level=xbmc.LOGINFO)
        return

    xbmc.log(f"Playing vidsrc {playback_url}", level=xbmc.LOGINFO)

    # Create a ListItem for playback
    list_item = xbmcgui.ListItem(path=playback_url)
    xbmcplugin.setResolvedUrl(handle=ADDON_HANDLE, succeeded=True, listitem=list_item)


params = parse_qs(sys.argv[2][1:])
action = params.get('action', [None])[0]
page = int(params.get('page', [1])[0])

xbmc.log(f"Action: {action}", level=xbmc.LOGINFO)

if action is None:
    main_menu()
elif action == 'trending':
    list_trending(page)
elif action == 'genres':
    list_genres()
elif action == 'movies_by_genre':
    genre_id = params['genre_id'][0]
    genre_name = params['genre_name'][0]
    list_movies_by_genre(genre_id, genre_name, page)
elif action == 'find':
    find_movies()
elif action == 'search':
    query = params['query'][0]
    search_movies(query, page)
elif action == 'play_movie':
    movie_id = params['id'][0]
    xbmc.log(f"Movie ID: {movie_id}", level=xbmc.LOGINFO)
    play_movie(movie_id)
