import xbmcgui
import xbmcplugin

from util.util import build_url, normalize_score

THUMB_BASE_URL = "https://image.tmdb.org/t/p/w185"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"


class Lister:
  def __init__(self, addon_handle, addon_base_url):
    self.__addon_handle = addon_handle
    self.__addon_base_url = addon_base_url

  def add_items(self, label_params_dict, playable=False):
    for label, params in label_params_dict.items():
      self.add_item(label, params, playable)

    xbmcplugin.endOfDirectory(self.__addon_handle)

  def add_item(self, label, params, playable=False):
    xbmcplugin.addDirectoryItem(
        self.__addon_handle,
        build_url(params, self.__addon_base_url),
        xbmcgui.ListItem(label),
        isFolder=(not playable)
    )

  def list_show(self, show, type, content_type='movies'):
    name = show['title'] if 'title' in show else show['name']
    release_year = show['release_date'][:4] \
      if 'release_date' in show and show['release_date'] else None
    if not release_year:
      release_year = show['first_air_date'][:4] \
        if 'first_air_date' in show and show['first_air_date'] else None

    title = f"{name} ({release_year if release_year else 'N/A'})"
    rating = f"{round(show['vote_average'], 2)} ({show['vote_count']})"
    normalized_rating = normalize_score(
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

    url = build_url(urlparams, self.__addon_base_url)
    xbmcplugin.addDirectoryItem(self.__addon_handle, url, list_item,
                                isFolder=True)
