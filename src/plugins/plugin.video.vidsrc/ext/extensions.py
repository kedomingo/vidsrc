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
  def __init__(self):
    super().__init__()
    self.playback_failed = False

  def onPlayBackStarted(self):
    xbmc.log("Playback started successfully.", xbmc.LOGINFO)

  def onPlayBackStopped(self):
    xbmc.log("Playback stopped.", xbmc.LOGINFO)

  def onPlayBackError(self):
    self.playback_failed = True
    xbmc.log("Playback error detected!", xbmc.LOGERROR)
