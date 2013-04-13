# post to twitter, facebook or other social media
import tweepy
import shorten

import requests as req

# Twitter auth info
CONSUMER_KEY = "***REMOVED***"
CONSUMER_SECRET = "***REMOVED***"

ACCESS_TOKEN = "***REMOVED***"
ACCESS_TOKEN_SECRET = "***REMOVED***"

# FB Info
FB_APP_ID = "***REMOVED***"
FB_APP_SECRET = "***REMOVED***"
FB_URL = "https://graph.facebook.com/me/accounts"
FB_TOKEN = "***REMOVED***"

def twitter_auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


def tweet_topic(topic):
    short_url = shorten.get_short(topic.get_comments_url())
    avail = 140 - 4 - len(short_url)
    cutoff = topic.title[:avail].rfind(' ')
    if len(topic.title) <= avail or cutoff == -1:
        cutoff = avail

    tweet = topic.title[:cutoff] + "... " + short_url
    return tweet

def fb_post(topic):
    r1 = req.get(FB_URL, params = {'access_token': FB_TOKEN})
    gd = find_gd(r1.json)
    r2 = req.post(gd_fb_url(gd), params = {'access_token': gd['access_token'],
                                           'message': topic.get_first_comment().comment,
                                           'link': topic.url,
                                           'caption': topic.title})
    return r2

def find_gd(response):
    for page in response['data']:
        if page['name'] == u'GreaterDebater':
            return page
        else:
            return None

def gd_fb_url(gdpage):
    return "https://graph.facebook.com/%s/feed" % gdpage['id']
