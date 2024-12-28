import base64
import re
import xbmc
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract_domain(url):
  try:
    # Parse the URL
    parsed_url = urlparse(url)
    # Get the domain name (netloc)
    domain = parsed_url.netloc

    # Handle cases where 'www.' is present or absent
    if domain.startswith('www.'):
      domain = domain[4:]  # Remove 'www.' if present

    return domain
  except Exception as e:
    xbmc.log(f"Error extracting domain: {e}", level=xbmc.LOGINFO)
    return None


def alg1(param):
  chars = []
  for count in range(0, len(param), 3):
    chars.append(param[count:count + 3])
  return ''.join(reversed(chars))


def alg4(param):
  rev = ''.join(reversed(param))
  partial = ''.join(
      map(lambda c: chr(ord(c) + (13 if c.lower() < 'n' else -13)), rev))
  rev = ''.join(reversed(partial))
  return base64.b64decode(rev).decode('utf-8')


def alg5(param):
  reversed_str = ''.join(reversed(param))
  result_str = ''
  for i in range(0, len(reversed_str), 2):
    result_str += reversed_str[i]
  return base64.b64decode(result_str).decode('utf-8')


def alg6(param):
  reversed_str = ''.join(reversed(param))
  hex_pairs = reversed_str.findall(r'.{1,2}')
  chars = [chr(int(pair, 16)) for pair in hex_pairs]
  key = "X9a(O;FMV2-7VO5x;Ao:dN1NoFs?j,"
  result_str = ''.join(
      chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(chars))
  return result_str


def alg7(param):
  reversed_str = ''.join(reversed(param))
  decremented_str = ''.join(chr(ord(c) - 1) for c in reversed_str)
  result_str = ''
  for i in range(0, len(decremented_str), 2):
    result_str += chr(int(decremented_str[i:i + 2], 16))
  return result_str


def alg8(param):
  extracted = param[10:-16]
  decoded = base64.b64decode(extracted).decode('utf-8')
  key = "3SAY~#%Y(V%>5d/Yg\"$G[Lh1rK4a;7ok" * (len(decoded) // len(key) + 1)[
                                              :len(decoded)]
  return ''.join(chr(ord(c1) ^ ord(c2)) for c1, c2 in zip(decoded, key))


def alg9(param):
  rot = {
    'x': 'a', 'y': 'b', 'z': 'c', 'a': 'd', 'b': 'e', 'c': 'f', 'd': 'g',
    'e': 'h', 'f': 'i', 'g': 'j', 'h': 'k', 'i': 'l', 'j': 'm', 'k': 'n',
    'l': 'o', 'm': 'p', 'n': 'q', 'o': 'r', 'p': 's', 'q': 't', 'r': 'u',
    's': 'v', 't': 'w', 'u': 'x', 'v': 'y', 'w': 'z', 'X': 'A', 'Y': 'B',
    'Z': 'C', 'A': 'D', 'B': 'E', 'C': 'F', 'D': 'G', 'E': 'H', 'F': 'I',
    'G': 'J', 'H': 'K', 'I': 'L', 'J': 'M', 'K': 'N', 'L': 'O', 'M': 'P',
    'N': 'Q', 'O': 'R', 'P': 'S', 'Q': 'T', 'R': 'U', 'S': 'V', 'T': 'W',
    'U': 'X', 'V': 'Y', 'W': 'Z'
  }

  return re.sub(r'[xyzabcdefghijklmnopqrstuvwXYZABCDEFGHIJKLMNOPQRSTUVW]',
                lambda match: rot[match.group(0)], param)


def alg10(encoded_param):
  reversed_str = encoded_param[::-1]
  cleaned = reversed_str.replace('-', '+').replace('_', '/')
  cleaned_binary = base64.b64decode(cleaned).decode('utf-8')
  result = ''.join(chr(ord(char) - 5) for char in cleaned_binary)
  return result


def alg11(param):
  reversed_str = ''.join(reversed(param))
  modified_str = reversed_str.replace('-', '+').replace('_', '/')
  decoded_str = base64.b64decode(modified_str).decode('utf-8')
  result_str = ''.join(chr(ord(c) - 7) for c in decoded_str)
  return result_str


def alg12(param):
  # Reverse the string
  reversed_param = param[::-1]

  # Subtract 1 from each character's char code
  encoded = ''.join(chr(ord(char) - 1) for char in reversed_param)

  # Decode the result by parsing pairs of hex digits
  result = ''.join(
      chr(int(encoded[i:i + 2], 16)) for i in range(0, len(encoded), 2))

  return result


def alg13(param):
  reversed_str = ''.join(reversed(param))
  modified_str = reversed_str.replace('-', '+').replace('_', '/')
  decoded_str = base64.b64decode(modified_str).decode('utf-8')
  result_str = ''.join(chr(ord(c) - 3) for c in decoded_str)
  return result_str


def decode_bruteforce(str_to_decode):
  for i in range(1, 20):
    try:
      function_to_call = f"alg{i}"
      xbmc.log(f"Trying {function_to_call}", level=xbmc.LOGINFO)
      func_to_call = globals()[function_to_call]
    except Exception:
      xbmc.log(f"Function alg{i} does not exist", level=xbmc.LOGINFO)
      pass
    else:
      xbmc.log(f"Calling alg{i}", level=xbmc.LOGINFO)
      try:
        result = func_to_call(str_to_decode)
        if str(result).startswith("http"):
          xbmc.log("decode success", level=xbmc.LOGINFO)
          return result
      except Exception:
        pass
  xbmc.log("decode failed", level=xbmc.LOGINFO)
  return None


def resolve(movie_id):
  url = f"https://vidsrcme.vidsrc.icu/embed/movie?tmdb={movie_id}&autoplay=1"

  # Step 1: Fetch the HTML content of the page
  headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Referer': url
  }
  response = requests.get(url, headers=headers)
  if response.status_code >= 400:
    xbmc.log(f"Request to {url} failed", level=xbmc.LOGINFO)
    return None

  soup = BeautifulSoup(response.text, 'html.parser')

  iframe1 = soup.find('iframe', id="player_iframe")
  if not iframe1:
    xbmc.log(f"CDN iframe not found from {url}.", level=xbmc.LOGINFO)
    return None

  iframe1src = iframe1.get("src")
  if not iframe1src:
    xbmc.log("CDN iframe src attribute not found.", level=xbmc.LOGINFO)
    return None

  iframe1src = 'http://' + iframe1src.lstrip('/')
  headers['Referer'] = iframe1src
  response = requests.get(iframe1src, headers=headers)
  if response.status_code >= 400:
    xbmc.log(f"Request to {iframe1src} failed", level=xbmc.LOGINFO)
    return None

  soup = BeautifulSoup(response.text, 'html.parser')

  # Step 4: Find the <script> tag and extract the JSON object based on the variable name in data-localize
  script_tags = soup.find_all('script', string=True)
  jumpsrc = None
  for script in script_tags:
    src = re.search(r"src: '/([^']+)'", script.text)
    if src:
      jumpsrc = src.group(1)
    else:
      xbmc.log(f"FAILED {script.text}.", level=xbmc.LOGINFO)

  if not jumpsrc:
    message = f"Jump src not found from {iframe1src}."
    xbmc.log(message, level=xbmc.LOGINFO)
    raise Exception(message)

  jumpsrc = 'http://' + extract_domain(iframe1src) + '/' + jumpsrc

  # jumpsrc = 'http://localhost:7070'
  response = requests.get(jumpsrc, headers=headers)
  if response.status_code >= 400:
    message = f"Request to {jumpsrc} failed"
    xbmc.log(message, level=xbmc.LOGINFO)
    raise Exception(message)

  soup = BeautifulSoup(response.text, 'html.parser')

  script_tags = soup.find_all('script')
  jumpsrc = None
  urldiv = None
  for script in script_tags:
    if not script.get('src'):
      continue
    jquerytag = re.search(r"jquery\.min\.js$", script.get('src'))
    if jquerytag:
      urldiv = script.find_previous_sibling()
      break

  if not urldiv:
    message = f"Could not find the file location to decode from {jumpsrc}"
    xbmc.log(message, level=xbmc.LOGINFO)
    raise Exception(message)

  decoded = decode_bruteforce(urldiv.text)
  if not decoded:
    message = "Could not find algorithm to decode file URL"
    xbmc.log(f"{message} {urldiv.text} {response.text}", level=xbmc.LOGINFO)
    raise Exception(message)

  return decoded
