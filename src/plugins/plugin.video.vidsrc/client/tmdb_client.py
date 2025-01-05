import requests
import hashlib

from urllib.parse import quote

from util.util import log, build_url, append_dicts
from util.cache import get_cached, cache_response

BASE_URL = "https://api.themoviedb.org/3"


class TmdbClient:
  def __init__(self, api_key):
    self.api_key = api_key


  def list_genres(self, type):
    cached = get_cached(cache_key=type, cache_group='genre')
    if cached:
      log(f"genre::{type}- cache hit")
      return cached

    url = f"{BASE_URL}/genre/{type}/list?api_key={self.api_key}"
    data = self.__get(url)
    cache_response(type, data, cache_group='genre')

    return data


  def trending(self, type, page=1):
    cachekey = f'{type}.{page}'
    cached = get_cached(cache_key=cachekey, cache_group='trending',
                        not_older_than_days=7)
    if cached:
      log(f"trending::{cachekey}- cache hit")
      return cached

    url = f"{BASE_URL}/trending/{type}/day?api_key={self.api_key}&page={page}"
    data = self.__get(url)
    cache_response(cachekey, data, cache_group='trending')

    return data


  def discover(self, type, params, page=1):
    cachekey = hashlib.md5(str(params).encode()).hexdigest()
    cachekey = f'{cachekey}.{page}'

    cached = get_cached(cache_key=cachekey, cache_group='discover',
                        not_older_than_days=14)
    if cached:
      log(f"discover- cache hit")
      return cached

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

    data = self.__get(url)
    cache_response(cachekey, data, cache_group='discover')
    log(f'cached {cachekey}')

    return data


  def search(self, type, query, page=1):
    url = f"{BASE_URL}/search/{type}?api_key={self.api_key}&query={quote(query)}&page={page}"
    return self.__get(url)


  def show_details(self, type, tmdb_id):
    """
    show movie details if type=movie, get details + seasons if type=tv
    """
    cachekey = f'{type}.{tmdb_id}'
    cached = get_cached(cache_key=cachekey, cache_group='show_details')
    if cached:
      log(f"show_details::{cachekey} cache hit")
      return cached

    url = f"{BASE_URL}/{type}/{tmdb_id}?api_key={self.api_key}"
    data = self.__get(url)
    cache_response(cachekey, data, cache_group='show_details')
    return data


  def season_details(self, tmdb_id, season_number):
    """
    get season details + episodes
    """
    cached = get_cached(cache_key=tmdb_id, cache_group='season_details')
    if cached:
      log(f"season_details::{tmdb_id} cache hit")
      return cached

    log(f"season_details::{tmdb_id} cache miss")
    url = f"{BASE_URL}/tv/{tmdb_id}/season/{season_number}?api_key={self.api_key}"
    data = self.__get(url)
    cache_response(tmdb_id, data, cache_group='season_details')

    return data


  def __get(self, url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
