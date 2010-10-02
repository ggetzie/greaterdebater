import BeautifulSoup as BS

for line in subxml.findAll('outline'):
    try:
        print line['xmlurl']
    except:
        pass

for line in lines:
    if line['title'] == "AnandTech": switch = True
    if line['title'] == "tips": switch = False
    if switch:
        try:
            print line['xmlurl']
            sources.write(line['xmlurl'])
        except:
            pass
