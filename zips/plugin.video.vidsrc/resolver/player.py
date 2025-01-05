import xbmc
import xbmcgui
import xbmcplugin

from ext.extensions import MyPlayer, PlaybackMonitor
from model.season import Show
from util.cache import get_cached
from util.util import log, show_notification, build_url, append_dicts


class Player:
  def __init__(self, addon_handle, addon_base_url, fs_client):
    self.__addon_handle = addon_handle
    self.__addon_base_url = addon_base_url
    self.__fs_client = fs_client

  def play_movie(self, params, tries=0):
    tmdb_id = params['tmdb_id']
    resolver = params['resolver'] if 'resolver' in params else None
    log(f"Resolving {tmdb_id}")

    playback_url = None
    subtitles = None
    error_message = None

    message = f'{tries + 1}: Resolving {tmdb_id}'
    back_url = next_url = None
    if 'episode_number' in params:
      request_params = {
        'episode_number': params['episode_number'],
        'season_number': params['season_number'],
        'tv_id': tmdb_id,
      }
      message += f" ep. {params['episode_number']}"
      seasondata = get_cached(cachekey=params['tmdb_id'], cachegroup='seasons')
      show = Show.from_dict(seasondata)
      # back and next buttons
      back_season, back_ep = show.get_back_button_episode(params['season_number'], params['episode_number'])
      next_season, next_ep = show.get_next_button_episode(params['season_number'], params['episode_number'])

      if back_season is not None and back_ep is not None:
        back_url = build_url(
            append_dicts(
                params,
                {
                  'season_number': back_season,
                  'episode_number': back_ep
                }
            ),
            self.__addon_base_url
        )

      if next_season is not None and next_ep is not None:
        next_url = build_url(
            append_dicts(
                params,
                {
                  'season_number': next_season,
                  'episode_number': next_ep
                }
            ),
            self.__addon_base_url
        )

    else:
      request_params = {'movieid': tmdb_id, }

    if resolver:
      request_params['resolver'] = resolver
      message += f' via {resolver}'

    if tries > 0:
      request_params['nocache'] = 1

    try:
      show_notification('Info', message)
      data = self.__fs_client.scrape(request_params)
      error_message = data['error'] if 'error' in data else None

      if not error_message:
        show_notification('Success', 'rendering')
        playback_url = data['playlist'] if 'playlist' in data else None
        log(f"Got playback url {playback_url}")
        subtitles = data['subtitles'] if 'subtitles' in data else None
    except Exception as e:
      error_message = f"- {e}"

    if playback_url is None:
      show_notification("Error",
                        f"Could not resolve movie {tmdb_id} {error_message}")
      log(f"Could not resolve movie {tmdb_id}")
      return

    log(f"Playing {playback_url}")

    # Create a ListItem for playback
    list_item = xbmcgui.ListItem(path=playback_url)
    xbmcplugin.setResolvedUrl(
        handle=self.__addon_handle,
        listitem=list_item,
        succeeded=True,
    )

    player = MyPlayer(previous_media_url=back_url, next_media_url=next_url)
    player.play(playback_url, list_item)
    monitor = PlaybackMonitor()

    self.set_subtitles(subtitles, player)
    # Retry once on failure
    if tries == 0:
      self.handle_retry_on_failure(tmdb_id, tries, player, monitor)

  def set_subtitles(self, subtitles, player: xbmc.Player):
    if subtitles:
      while not player.isPlaying():
        xbmc.sleep(100)

      if len(subtitles) == 1:
        engsub = str(subtitles[0])
        if engsub.startswith('/'):
          engsub = self.__fs_client.subtitle(engsub)
        log(f"Found engsub {engsub}")
        player.setSubtitles(engsub)
        return

      # no choice - display all - add in reverse order
      log(f"Adding all {len(subtitles)} subs")
      for subtitle_url in subtitles[::-1]:
        player.setSubtitles(subtitle_url)

  def handle_retry_on_failure(
      self,
      tmdb_id,
      tries,
      player: xbmc.Player,
      monitor: xbmc.Monitor
  ):
    while not monitor.abortRequested():
      if monitor.waitForAbort(1):
        break
      if player.isPlaying():
        log("Item is playing!")
        break

    if player.playback_failed or monitor.playback_failed:
      self.play_movie(tmdb_id, tries=tries + 1)
