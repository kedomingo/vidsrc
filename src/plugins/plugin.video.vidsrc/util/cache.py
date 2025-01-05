import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path

from util.util import log


def get_cached(cachekey, cachegroup=None, disregard_date=False):
  cachegroup = cachegroup if cachegroup is not None else str(cachekey)[0]
  file_path = get_cache_path(cachekey, cachegroup)
  if not os.path.isfile(file_path):
    return None

  with open(file_path, 'r') as file:
    data = json.load(file)

  if disregard_date:
    return data['body']

  year, month, day = map(int, data['cached'].split("-"))
  cached_on = datetime(year, month, day).date()
  today = datetime.today().date()
  days_elapsed = (today - cached_on).days
  if days_elapsed <= 2:
    return data['body']

  return None


def cache_response(cachekey, response, cachegroup=None):
  cachegroup = cachegroup if cachegroup is not None else str(cachekey)[0]
  file_path = get_cache_path(cachekey, cachegroup)

  directory = os.path.dirname(file_path)
  if not os.path.exists(directory):
    os.makedirs(directory)

  with open(file_path, 'w') as handle:
    payload = {'cached': str(datetime.today().date()), 'body': response}
    handle.write(json.dumps(payload))
    log(f'Written {file_path}')

  cleanup()


def get_cache_path(cachekey, cachegroup):
  today = str(datetime.today().date())
  filename = f'{cachegroup}/{cachekey}.json'
  return f"{get_cache_dir()}/{today}/{filename.lstrip('/')}"


def get_cache_dir():
  return f"{tempfile.gettempdir()}/cache"


def cleanup():
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

        if (today - folder_date).days > 30:
          shutil.rmtree(folder)
      except Exception as e:
        continue
