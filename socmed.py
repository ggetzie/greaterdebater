# post to twitter, facebook or other social media
import tweepy
import shorten

CONSUMER_KEY = "***REMOVED***"
CONSUMER_SECRET = "***REMOVED***"

ACCESS_TOKEN = "***REMOVED***"
ACCESS_TOKEN_SECRET = "***REMOVED***"


def twitter_auth():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    return api


def tweet_topic(topic):
    short_url = shorten.get_short(topic.get_absolute_url())
    avail = 140 - 4 - len(short_url)
    cutoff = topic.title[:avail].rfind(' ')
    if len(topic.title) <= avail or cutoff == -1:
        cutoff = avail

    tweet = topic.title[:cutoff] + "... " + short_url
    return tweet
    

