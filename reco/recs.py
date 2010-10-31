import BeautifulSoup as BS
import feedparser
import clusters

# for line in subxml.findAll('outline'):
#     try:
#         print line['xmlurl']
#     except:
#         pass

# for line in lines:
#     if line['title'] == "AnandTech": switch = True
#     if line['title'] == "tips": switch = False
#     if switch:
#         try:
#             print line['xmlurl']
#             sources.write(line['xmlurl'])
#         except:
#             pass


# 1. get word vectors for all entries
# 2. compute similarity between each entry and all other entries
# 3. Similarity class, entry1, entry2, similarity
# 4. Sort the list of similarities from highest to lowest
# 5. Take all the similarities above a certain threshold
# 6. Group all the entries that are transitively similar.
#    i.e. A ~ B ~ C -> A, B, C are all in a group
#    probably A and C will be similar as well?

class Similarity():
    
    def __init__(self, e1, e2, score):
        self.e1 = e1
        self.e2 = e2
        self.score = score


class SourceFeed():

    def __init__(self, url, agg):
        self.url = url
        self.agg = agg
        d = feedparser.parse(url)
        self.title = d.feed['title']

class Entry():

    def __init__(self, title, url, data):
        self.title = title
        self.url = url
        self.data = data

def calc_sims(data):
    sims = []
    
    for i in range(len(data)):
        for j in range(i+1, len(data)):
            sims.append(Similarity(e1=i,
                                   e2=j,
                                   score=clusters.pearson(data[i],data[j])))
    return sims
    

