import xbmc
import xbmcgui


class PlaybackMonitor(xbmc.Monitor):
  def __init__(self):
    super().__init__()
    self.playback_failed = False

  def onNotification(self, sender, method, data):
    if method == "Player.OnStop" and "error" in data.lower():
      self.playback_failed = True
      xbmc.log("Playback failed!", xbmc.LOGERROR)


class MyPlayer(xbmc.Player):
  def __init__(self, previous_media_url=None, next_media_url=None):
    super().__init__()
    self.playback_failed = False
    self.previous_media_url = previous_media_url
    self.next_media_url = next_media_url

  def onPlayBackStarted(self):
    xbmc.log("Playback started successfully.", xbmc.LOGINFO)
    if self.next_media_url:
      xbmc.executebuiltin(f'Action(CycleNext, {self.next_media_url})')
    if self.previous_media_url:
      xbmc.executebuiltin(f'Action(CyclePrevious, {self.previous_media_url})')

  def onPlayBackStopped(self):
    xbmc.log("Playback stopped.", xbmc.LOGINFO)

  def onPlayBackError(self):
    self.playback_failed = True
    xbmc.log("Playback error detected!", xbmc.LOGERROR)
