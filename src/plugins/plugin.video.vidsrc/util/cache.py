import json
import os
import shutil
import random
from datetime import datetime
from pathlib import Path

import xbmcvfs
from util.util import log


def cache_get(cache_key, cache_group=None, not_older_than_days=-1):
  cache_group = cache_group if cache_group is not None else str(cache_key)[0]
  file_path = get_cache_path(cache_key, cache_group)
  if not os.path.isfile(file_path):
    return None

  with open(file_path, 'r') as file:
    data = json.load(file)

  if not_older_than_days < 0:
    return data['body']

  year, month, day = map(int, data['cached'].split("-"))
  cached_on = datetime(year, month, day).date()
  today = datetime.today().date()
  days_elapsed = (today - cached_on).days
  if days_elapsed <= not_older_than_days:
    return data['body']

  return None


def cache_put(cache_key, response, cache_group=None):
  cache_group = cache_group if cache_group is not None else str(cache_key)[0]
  file_path = get_cache_path(cache_key, cache_group)

  directory = os.path.dirname(file_path)
  if not os.path.exists(directory):
    os.makedirs(directory)

  with open(file_path, 'w') as handle:
    payload = {'cached': str(datetime.today().date()), 'body': response}
    handle.write(json.dumps(payload))
    log(f'Written {file_path}')

  # cleanup 20% of the time
  if (random.random() * 1000) < 200:
    __cleanup()


def get_cache_path(cachekey, cachegroup):
  today = str(datetime.today().date())
  filename = f'{cachegroup}/{cachekey}.json'
  return f"{get_cache_dir()}/{today}/{filename.lstrip('/')}"


def get_cache_dir():
  tempdir = xbmcvfs.translatePath("special://temp/")
  tempdir = str(tempdir).rstrip('/')
  return f"{tempdir}/cache"


def __cleanup():
  """
  delete cache older than 30 days
  """
  cache_dir = get_cache_dir()
  today = datetime.today().date()

  for folder in Path(cache_dir).iterdir():
    if folder.is_dir():
      try:
        year, month, day = map(int, folder.name.split("-"))
        folder_date = datetime(year, month, day).date()

        if (today - folder_date).days > (30 * 6): # 6 months
          shutil.rmtree(folder)
      except Exception as e:
        continue
