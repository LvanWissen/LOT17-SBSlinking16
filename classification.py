import re
import string
import copy
from nltk.corpus import stopwords
from fuzzywuzzy import process
from nltk import word_tokenize

from classification import classify
from stanford import constituencyparser, NERtagger

def candidate_extractor(message, use_np=False):
    
    text = message["text"]
    print(text)
    
    stoplist = stopwords.words()    
    stop = "|".join(stoplist)
    
    sentences = sent_tokenize(text)
    first_words = [w[0] for w in [word_tokenize(s) for s in sentences]]
    print(first_words)
    
    # REGEX Capitalization
    match = re.findall("(?:[{upper}]\w*(?:'s)?\s(?:(?:(?:{stop}) )*))*[{upper}]\w*".format(upper=string.ascii_uppercase, stop=stop), text)
    match = list(set(match))
    
    matchcopy = copy.deepcopy(match)
    
    for m in matchcopy:
        if 'by' in m:
            match.append(m.rsplit(' by ')[0])
            match.remove(m)
            
        print(m)
        
        if len(m.split()) == 1 and m in first_words:
            print(m)
            match.remove(m)
            
    
    # USE NP'S AS BOOKTITLES
    if use_np:
        trees = constituencyparser(text)
        nps = []
        for tree in trees:
            tree = list(tree)[0]
            nps += [j for j in [" ".join(i.leaves()) for i in tree[0].subtrees() if i.label() == 'NP'] if j.count(' ') > 0]

        for np in nps:
            if 'by' in np:
                nps.append(np.rsplit(' by ')[0])

        matches = [m for m in match if m.lower() not in stoplist and m in nps]
                
    else:
        matches = [m for m in match if m.lower() not in stoplist]

    
    
    return matches
    
def find_authors(text, match, windowsize=5):
    """
    Find author names (Entity Type = PERSON) within a
    windowsize (default = 5) of a matchphrase in a text.
    
    Uses the Stanford NERtagger to process pieces of text. 
    Returns all person names as a list for every occurence in the text. 
    """
    
    matchwords = word_tokenize(match)
    
    nersequence = NERtagger(text)
    tokens, etypes = zip(*nersequence)
    
    values = np.array(tokens)
    
    startindices = np.where(values == matchwords[0])
    endindices = np.where(values == matchwords[-1])
    
    indices = []
    for s in list(startindices)[0]:
        for e in list(endindices)[0]:
            if e-len(matchwords)+1 == s:
                start, end = int(s), int(e)
                indices.append((start,end))
    
    all_authors = []
    
    for index in set(indices):
        start, end = index
        
#         window = tokens[start-windowsize:start] + tokens[end+1:end+1+windowsize]
#         windowtags = etypes[start-windowsize:start] + etypes[end+1:end+1+windowsize]
#         windowrange = list(range(start-windowsize, start)) + list(range(end+1, end+1+windowsize))
        
        startwindow = start-windowsize
        if startwindow < 0:
            startwindow = 0
    
        window = tokens[startwindow:end+windowsize+1]
        windowtags = etypes[startwindow:end+windowsize+1]
        windowrange = list(range(startwindow,end+windowsize+1))
        
#         authors_index = [(i[0],i[2]) for i in zip(window, windowtags, windowrange) if i[1] == 'PERSON']
        
        authors = []
        for token, etype, index in zip(window, windowtags, windowrange):
            if etype == 'PERSON':
                authors.append(token)
            else:
                if authors:
                    all_authors.append(" ".join(authors))
                    authors = []
            
        
    return all_authors
        

def get_titles(c, d):
    
    title_candidates = set()
    
    for word in word_tokenize(c.lower()):
        if word in stopwords.words() or word == "'s":
            continue
        
        try:
            title_candidates.update(d[word])
        except:
            print(c, "not part of a title")        
        
    return title_candidates


def classify(message, d, treshold=90):
    """
    """
    
    ids = []
    candidates = candidate_extractor(message)
    
    for c in candidates:        
        matchlist = get_titles(c, d)
        
        authors = find_authors(message["text"], c)
        
        # DISCARD ALL CANDIDATES THAT ARE NAMES
        if c in authors:
            continue
        
        authors = " ".join(authors)
        
        c = str(tuple((c, authors)))
        
        if matchlist:
            titles, authors, works = zip(*matchlist)
                     
            print(c)
            (title, author), confidence = process.extractOne(c, zip(titles,authors))
            workid = works[titles.index(title)]
            print(title, authors[titles.index(title)], workid, sep=', ')
            
            if confidence >= treshold:
                ids.append((workid, confidence))
            
    return sorted(ids, key=lambda x: x[1], reverse=True)