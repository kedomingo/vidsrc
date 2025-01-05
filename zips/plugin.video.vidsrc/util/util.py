import json
import math
import xbmc
import xbmcgui
from urllib.parse import urlencode


def build_url(query, base):
  prepared_query = {}
  for k, v in query.items():
    if isinstance(v, dict):
      prepared_query[k] = json.dumps(v)
    else:
      prepared_query[k] = v
  return f"{base}?{urlencode(prepared_query)}"


def log(message, level=xbmc.LOGINFO):
  xbmc.log(str(message), level)


def show_notification(title, message):
  # Create a dialog box with a title and message
  xbmcgui.Dialog().notification(title, message, xbmcgui.NOTIFICATION_INFO, 5000)


def append_dicts(dict1, dict2):
  copy = dict1.copy()
  copy.update(dict2)
  return copy


def normalize_score(popularity, reviews, review_score):
  if reviews <= 22:
    review_factor = 0.55 + (0.0005 * reviews * reviews)
  else:
    # math.log is base e by default. but we want to be explicit
    review_factor = 0.3 * math.log(reviews - 9, math.e)
  review_factor = min(review_factor, 1.2)

  # popularity does not affect score if low enough, reviews will affect solely
  if popularity <= 300:
    popularity_factor = 1
    review_factor = min(1, review_factor)
  else:
    popularity_factor = min(1, (popularity + 100) / (450 * review_factor))

  review_factor = min(1.07, review_factor)

  # Final score calculation
  return round(
      max(0, min(review_score * review_factor * popularity_factor, 10)), 2)

