import xbmc
import xbmcgui

from util.cache import cache_put, cache_get


class PlaybackMonitor(xbmc.Monitor):
  def __init__(self):
    super().__init__()
    self.playback_failed = False


  def onNotification(self, sender, method, data):
    if method == "Player.OnStop" and "error" in data.lower():
      self.playback_failed = True
      xbmc.log("Playback failed!", xbmc.LOGERROR)


class MyPlayer(xbmc.Player):
  def __init__(self, media_type, media_id, previous_media_url=None,
      next_media_url=None):
    self.media_type = media_type
    self.media_id = media_id
    self.playback_failed = False
    self.previous_media_url = previous_media_url
    self.next_media_url = next_media_url


  def onPlayBackStarted(self):
    xbmc.log("Playback started successfully.", xbmc.LOGINFO)
    cached_position_seconds = cache_get(
        f'{self.media_type}-{self.media_id}',
        'last-position',
        not_older_than_days=30
    )
    if cached_position_seconds:
      xbmc.log(f'Auto-seek to {cached_position_seconds}', xbmc.LOGINFO)
      self.seekTime(cached_position_seconds)

  def onPlayBackError(self):
    self.playback_failed = True
    xbmc.log("Playback error detected!", xbmc.LOGERROR)
