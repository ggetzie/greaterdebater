from pydelicious import get_popular, get_userposts, get_urlposts
import time
import recommendations as rec

def initializeUserDict(tag, count=5):
    user_dict={}
    
    # get the top "count" popular posts
    for p1 in get_popular(tag=tag)[0:count]:
        # find all users who posted this
        for p2 in get_urlposts(p1['href']):
            user = p2['user']
            user_dict[user] = {}
    return user_dict

def fillItems(user_dict):
    all_items={}
    # Find links posted by all users
    for user in user_dict:
        for i in range(3):
            try: 
                posts = get_userposts(user)
                break
            except:
                print "Failed user " + user + ", retrying"
                time.sleep(4)

        for post in posts:
            url=post['href']
            user_dict[user][url] = 1.0
            all_items[url] = 1
    
    # Fill in missing items with 0
    for ratings in user_dict.values():
        for item in all_items:
            if item not in ratings:
                ratings[item] = 0.0

def initializeTagDict(count=5):
    tag_dict = {}
    # get the top "count" popular posts
    for p1 in get_popular()[0:count]:
        # get all the tags for each post
        tags = p1['tags'].split(' ')
        for tag in tags:
            if tag not in tag_dict.keys():
                tag_dict[tag] = {}
    return tag_dict
    

def fillTagDict(tag_dict, count=5):
    all_items = {}

    # find "count" popular links with each tag
    for tag in tag_dict:
        for i in range(3):
            try:
                posts = get_popular(tag=tag)[0:count]
                break
            except:
                print "Failed tag" + tag + ", retrying"
                time.sleep(4)
        for post in posts:
            url = post['href']
            tag_dict[tag][url] = 1.0
            all_items[url] = 1

    for ratings in tag_dict.values():
        for item in all_items:
            if item not in ratings:
                ratings[item] = 0.0

def findmost(simtags):
    # given a dictionary of tags and their top matches, find the tag whose
    # top match is most similar
    
    result = []
    top_score = 0

    for tag in simtags:        
        if simtags[tag][0][0] > top_score:
            top_score = simtags[tag][0][0]
            result = [tag]
        elif simtags[tag][0][0] == top_score:
            result.append(tag)
        
    print "top_score: %f \nTags:" % top_score
    
    for tag in result:
        print "%s, %s" % (tag, simtags[tag][0][1])
        
def printmatches(tags, tag):
    # Prints all of the urls that have a given tag
    for item in tags[tag]:
        if tags[tag][item] == 1.0: print item


