import xbmc


class PlaybackMonitor(xbmc.Monitor):
  def __init__(self):
    super().__init__()
    self.playback_failed = False


  def onNotification(self, sender, method, data):
    if method == "Player.OnStop" and "error" in data.lower():
      self.playback_failed = True
      xbmc.log("Playback failed!", xbmc.LOGERROR)


class MyPlayer(xbmc.Player):
  def __init__(
      self,
      play_from_seconds=None,
      previous_media_url=None,
      next_media_url=None
  ):
    self.play_from_seconds = play_from_seconds
    self.previous_media_url = previous_media_url
    self.next_media_url = next_media_url
    self.playback_failed = False


  def onPlayBackStarted(self):
    xbmc.log("Playback started successfully.", xbmc.LOGINFO)

    if self.play_from_seconds is not None:
      xbmc.log(f'Auto-seek to {self.play_from_seconds}', xbmc.LOGINFO)
      self.seekTime(self.play_from_seconds)


  def onPlayBackError(self):
    self.playback_failed = True
    xbmc.log("Playback error detected!", xbmc.LOGERROR)
