import requests
from urllib.parse import quote

from util.util import log, build_url, append_dicts

BASE_URL = "https://api.themoviedb.org/3"


class TmdbClient:
  def __init__(self, api_key):
    self.api_key = api_key

  def list_genres(self, type):
    url = f"{BASE_URL}/genre/{type}/list?api_key={self.api_key}"
    return self.__get(url)

  def trending(self, type, page=1):
    url = f"{BASE_URL}/trending/{type}/day?api_key={self.api_key}&page={page}"
    return self.__get(url)

  def discover(self, type, params, page=1):
    request = {'api_key': self.api_key}

    if 'genre_all' not in params:
      if 'genre_id' in params:
        request['with_genres'] = params['genre_id']

    if 'date_all' not in params:
      if 'date_gte' in params:
        if type == 'tv':
          request['first_air_date.gte'] = params['date_gte']
        else:
          request['primary_release_date.gte'] = params['date_gte']
      if 'date_lte' in params:
        if type == 'tv':
          request['first_air_date.lte'] = params['date_lte']
        else:
          request['primary_release_date.lte'] = params['date_lte']

    request['sort_by'] = 'popularity.desc'

    url = build_url(
        append_dicts({'page': page}, request),
        f"{BASE_URL}/discover/{type}"
    )
    log(f"Discover URL {url}")

    return self.__get(url)

  def search(self, type, query, page=1):
    url = f"{BASE_URL}/search/{type}?api_key={self.api_key}&query={quote(query)}&page={page}"
    return self.__get(url)

  def show_details(self, type, tmdb_id):
    """
    show movie details if type=movie, get details + seasons if type=tv
    """
    url = f"{BASE_URL}/{type}/{tmdb_id}?api_key={self.api_key}"
    return self.__get(url)

  def season_details(self, tmdb_id, season_number):
    """
    get season details + episodes
    """
    url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_number}?api_key={self.api_key}"
    return self.__get(url)

  def __get(self, url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
