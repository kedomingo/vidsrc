import json
import requests

from util.util import log, build_url

BASE_URL = "https://api.themoviedb.org/3"

# SERVER_ADDRESS = 'http://firestreamarr.xyz:8080'
SERVER_ADDRESS = 'http://localhost:8080'

class FirestreamarrClient:

  def scrape(self, request_params):
    server_url = build_url(request_params, f'{SERVER_ADDRESS}/fetch')
    log(f'Server URL {server_url}')

    result = requests.get(server_url)
    log(f"Got response {result.text}")
    return json.loads(result.text)

  def subtitle(self, path):
    return f'{SERVER_ADDRESS}{path}'
