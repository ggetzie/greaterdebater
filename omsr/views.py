# from gdutils.scrape import get
import urllib2, gzip, StringIO

# from omsr.models import Tweet
from settings import DATA_DIR
OMURL = 'http://api.twitter.com/statuses/user_timeline.xml?screen_name=oldmansearch'

def get(url):
    request = urllib2.Request(url)
    request.add_header("Accept-encoding", "gzip")
    request.add_header("User-Agent", "GreaterDebater Web Scraper - contact: admin@greaterdebater.com")
    usock = urllib2.urlopen(request)
    response = usock.read()
    if usock.headers.get('content-encoding', None) == 'gzip':
        response = gzip.GzipFile(fileobj=StringIO.StringIO(response)).read()
    return response

def tweets(request):
    # fetch the tweets from @oldmansearch
    call_log = open(DATA_DIR + 'tweettime')
    last_call = call_log.read()
    tweets = get(OMURL)
    pass

def results(request, keywords):
    # show the search results from google for a given tweet
    pass
