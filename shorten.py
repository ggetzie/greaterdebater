# Shorten urls with goo.gl
import requests
import json

CLIENT_ID = "***REMOVED***"
CLIENT_SECRET = "***REMOVED***"
API_KEY = "***REMOVED***"
GOOGL = "https://www.googleapis.com/urlshortener/v1/url"


def get_short(url):
    data = {'longUrl': url}
    headers = {'Content-Type': 'application/json'}
    target = "%s?key=%s" % (GOOGL, API_KEY)
    response = requests.post(target, data=json.dumps(data), headers=headers)
    return json.loads(response.text)['id']
    

def expand(url, projection="FULL"):
    target = "%s?key=%s&shortUrl=%s&projection=%s" % (GOOGL, API_KEY, url, projection)
    response = requests.get(target)
    return json.loads(response.text)
