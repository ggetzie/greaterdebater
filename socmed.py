# post to twitter, facebook or other social media
import tweepy
import shorten

import requests as req

# Twitter auth info
CONSUMER_KEY = "GoXTH8CmlDT02qrodoNRg"
CONSUMER_SECRET = "0ONK2ftM1KhVAqSaTx4mRoPk2E63L04scm5FPS3r54"

ACCESS_TOKEN = "267911310-2pMMpDPotFYgLFJKvkMdVqGZ3eZ1UQG3ZH1vVFns"
ACCESS_TOKEN_SECRET = "daipx4LEvBkuHgO3VVnkaZryFB2IFVQJppMsgJgZ64"

# FB Info
FB_APP_ID = "131901986893076"
FB_APP_SECRET = "633497271c15a280ab0aff366f1f3622"
FB_URL = "https://graph.facebook.com/me/accounts"
FB_TOKEN = "BAAB39tMS7RQBAFHD6335OtaY0BPFoQeZAsOP645tUKUolXfjGbdbUoo0J324sFepZA7qfGzWbhuwl5SuqBFgcLC0Va3SUzSHVLIeKZCi4dGKEs4HQk6ZAEb4QiDJSd9WxewDcaef5gmD52cOsa0Q2TEuZCJ1yURaIidakPoQcB4dM9oOeK1JbKPfT2ReUDVvjuXPgQ0O4zgZDZD"

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
    gd_fb_url = "https://graph.facebook.com/%s/feed" % gd['id']
    r2 = req.post(gd_fb_url, params = {'access_token': gd['access_token'],
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

