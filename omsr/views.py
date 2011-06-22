from gdutils.scrape import get

OMURL = 'http://api.twitter.com/statuses/user_timeline.xml?screen_name=oldmansearch'

def tweets(request):
    # fetch the tweets from @oldmansearch
    tweets = get(OMURL)
    pass

def results(request, keywords):
    # show the search results from google for a given tweet
    pass
