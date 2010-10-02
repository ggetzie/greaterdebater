import feedparser
import re

# Returns title and dictionary of word counts for an RSS feed
def getwordcounts(url):
    # parse the feed
    d = feedparser.parse(url)
    wc = {}

    # Loop over all the entries
    for e in d.entries:
        if 'summary' in e: summary = e.summary
        else: summary = e.description
        
        # Extract a list of words
        words = getwords(e.title + ' ' + summary)
        for word in words:
            wc.setdefault(word, 0)
            wc[word] += 1
    return d.feed.title, wc

def getentrywordcount(entry):
    wc = {}
    if 'summary' in entry: summary = entry.summary
    else: summary = entry.description
    words = getwords(entry.title + ' ' + summary)
    for word in words:
        wc.setdefault(word,0)
        wc[word] += 1
    return wc

def getwords(html):
    # Remove all the HTML tags
    txt = re.compile(r'<[^>]+>').sub('', html)

    # Split words by all non-alpha characters
    words = re.compile(r'[^A-Z^a-z]+').split(txt)
    
    # Convert to lowercase
    return [word.lower() for word in words if word != '']

def testfeeds(infile='data/feedlist.txt'):
    for url in file(infile):
        d = feedparser.parse(url)
        try:
            title = d.feed.title
            print title
        except AttributeError:
            print "Cannot find title for %s" % url

def saveentrydata(filename='data/entrydata.txt'):
    apcount = {}
    wordcounts = {}
    entrylist = []
    for feedurl in file('data/sources.txt'):
        d = feedparser.parse(feedurl)
        for e in d.entries:
            wc = getentrywordcount(e)
            entrylist.append(( e.title, d.feed.title))
            wordcounts[(e.title, d.feed.title)] = wc
            for word, count in wc.items():
                apcount.setdefault(word, 0)
                if count > 1:
                    apcount[word] += 1
    
    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc) / len(entrylist)
        if frac > 0.05 and frac < 0.1: wordlist.append(w)

    out = file(filename, 'w')
    out.write('Entry')
    for word in wordlist: out.write('\t%s' % word)
    out.write('\n')
    for entry, wc in wordcounts.items():
        entry_title = entry[0].encode('ascii', 'ignore')
        blog_title = entry[1].encode('ascii', 'ignore')
        out.write("%s | %s" % (entry_title, blog_title))
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')
    
        
if __name__ == "__main__":
    apcount = {}
    wordcounts = {}
    feedlist = []
    for feedurl in file('data/sources.txt'):
        feedlist.append(feedurl)
        title, wc = getwordcounts(feedurl)
        wordcounts[title] = wc
        for word, count in wc.items():
            apcount.setdefault(word, 0)
            if count > 1:
                apcount[word] += 1
                
    # select only words that appear in some maximum and minimum percentages of blogs
    wordlist = []
    for w, bc in apcount.items():
        frac = float(bc)/len(feedlist)
        if frac > 0.1 and frac < 0.5: wordlist.append(w)

    out = file('data/blogdata.txt', 'w')
    out.write('Blog')
    for word in wordlist: out.write('\t%s' % word)
    out.write('\n')
    for blog, wc in wordcounts.items():
        # deal with unicode outside the ascii range
        blog = blog.encode('ascii', 'ignore')
        out.write(blog)
        for word in wordlist:
            if word in wc: out.write('\t%d' % wc[word])
            else: out.write('\t0')
        out.write('\n')
