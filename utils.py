import datetime
import random
import types
import re

def random_string(length):
    """Returns an alphanumeric string of random characters with the given length"""
    alphanumeric = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    return ''.join([random.choice(alphanumeric) for x in range(length)])

def calc_start(page, paginate_by, count):
    """Calculate the first number in a section of a list of objects to be displayed as a numbered list"""
    if page is not None:
        if page == 'last':
            return paginate_by * (count / paginate_by) + 1
        else:
            return paginate_by * (int(page) - 1) + 1                
    else:
        return 1

def elapsed_time(dtime):
    delta = datetime.datetime.now() - dtime
    if delta.days > 7:
        return time_plural(delta.days / 7, "week")
    elif delta.days > 0:
        return time_plural(delta.days, "day")
    elif delta.seconds > 3600:
        return time_plural(delta.seconds / 3600, "hour")
    elif 3600 > delta.seconds >= 60:
        return time_plural(delta.seconds / 60, "minute")
    elif 60 > delta.seconds >= 1:
        return time_plural(delta.seconds, "second")
    elif delta.seconds == 0:
        return time_plural(delta.microseconds / 1000, "millisecond")
    else:
        return "0 milliseconds"

def time_plural(num, unit):
    if num == 1:
        return ''.join([str(num), " ", unit])
    else:
        return ''.join([str(num), " ", unit, "s"])

    
def tag_dict(tag_str):
    """returns a dictionary where keys are tags and values
    are the count of how many users have used that tag for
    this topic"""
    if tag_str == '':
        return {}
    else:
        kv = [row.split(',') for row in tag_str.split('\n')]        
        return dict(zip(kv[0], [int(s) for s in kv[1]]))

def tag_string(tag_d):
    """Takes a dictionary of tags and tag counts and returns
    a string in comma separated format"""
    tags = []
    counts = []
    tag_items = tag_d.items()
    if tag_items:
        tag_items.sort(cmp=lambda x, y: cmp(x[1], y[1]), reverse=True)
        for k, v in tag_items:
            tags.append(k)
            counts.append(v)
        return "\n".join([",".join(tags), 
                          ",".join([str(i) for i in counts])])
    else:
        return ''

def autolink(html):
    # match all the urls
    # this returns a tuple with two groups
    # if the url is part of an existing link, the second element
    # in the tuple will be "> or </a>
    # if not, the second element will be an empty string
    urlre = re.compile("(\(?https?://[-A-Za-z0-9+&@#/%?=~_()|!:,.;]*[-A-Za-z0-9+&@#/%=~_()|])(\">|</a>)?")
    urls = urlre.findall(html)
    clean_urls = []

    # remove the duplicate matches
    # and replace urls with a link
    for url in urls:
        # ignore urls that are part of a link already
        if url[1]: continue
        c_url = url[0]
        # ignore parens if they enclose the entire url
        if c_url[0] == '(' and c_url[len(c_url)-1] == ')':
            c_url = c_url[1:len(c_url)-1]


        if c_url in clean_urls: continue # We've already linked this url

        clean_urls.append(c_url)
        # substitute only where the url is not already part of a
        # link element.
        html = re.sub("(?<!(=\"|\">))" + re.escape(c_url), 
                      "<a rel=\"nofollow\" href=\"" + c_url + "\">" + c_url + "</a>",
                      html)
    return html

def remove_blank_tags(obj):
    """check a string of tags and tag counts for an entry where the
    tag is an empty string and remove that entry
    """
    if obj.tags:
        td = tag_dict(obj.tags)
        newtd = {}
        for k, v in td.items():
            if k:
                newtd[k] = v
        obj.tags = tag_string(newtd)
        obj.save()

def remove_blank_user_tags(ut):
    """check a string of tags and tag counts for an entry where the
    tag is an empty string and remove that entry
    """
    if ut.tags[0] == ',':
        ut.tags = ut.tags[1:]
    ut.tags = ut.tags.replace(',,', ',')
    ut.save()


def update_tags(oldtagstr, newtaglst):
    """oldtagstr is a string with a comma seperated list of tags and a
    comma seperated list of tag counts seperated by a newline.
    e.g. 'politics,funny,technology\n7,5,2' 
    
    newtaglst is a list of strings to be added, increment the count if

    if it's not.

    return a new string in the same format as oldtagstr with the new
    entries and counts
    """
    td = tag_dict(oldtagstr)
    for tag in newtaglst:
        if tag in td:
            td[tag] += 1
        else:
            td[tag] = 1
    return tag_string(td)

