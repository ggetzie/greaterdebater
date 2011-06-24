from django.db.models import Max
from django.shortcuts import render_to_response
from gdutils.scrape import get, getText

from omsr.models import Tweet, Account

import datetime
import xml.dom.minidom
OMURL = 'http://api.twitter.com/statuses/user_timeline.xml?screen_name=oldmansearch'



def tweets(request):
    # fetch the tweets from @oldmansearch
    account = Account.objects.get(screen_name='oldmansearch')
    delta_t = datetime.datetime.now() - account.last_checked
    if delta_t.seconds > 15*60:
        max_id = Tweet.objects.aggregate(Max('tweet_id'))['tweet_id__max']
        response = get(OMURL+ '&since_id=' + str(max_id))
        tweetdata = xml.dom.minidom.parseString(response)
        statuses = tweetdata.getElementsByTagName('status')
        for status in statuses:
            temp = Tweet(status = getText(status.getElementsByTagName('text')[0].childNodes),
                         tweet_id = int(getText(status.getElementsByTagName('id')[0].childNodes)),
                         tweeter = account)
            ca = getText(status.getElementsByTagName('created_at')[0].childNodes)
            cal = ca.split()
            utcoffset = cal[-2]
            temp.posted = datetime.datetime.strptime(ca, "%a %b %d %H:%M:%S " + utcoffset + " %Y")
            temp.save()
    
    return render_to_response('omsr_templates/tweets.html',
                              {'tweets': tweets,
                               'account': account},
                              context_instance=RequestContext(request))

def results(request, keywords):
    # show the search results from google for a given tweet
    pass
