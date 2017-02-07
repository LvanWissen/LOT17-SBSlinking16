# coding: utf-8

import os
import csv
import json
import dateutil.parser
from bs4 import BeautifulSoup
import pickle
import re
from nltk import word_tokenize

TRAINFOLDER = 'data/train/'
LABELFILETRAIN = 'data/sbs16mining-linking-training-labels.csv'
# LABELFILETEST = 'data/sbs16mining-linking-test-labels-librarything.csv'
LABELFILETEST = 'data/sbs16mining-linking-training-labels.csv'
METAFILE = 'data/sbs16mining.book-metadata.json'
TESTFOLDER = 'data/train/'



def main():
    """
    :return:
    """

def threadparser(location):
    """
    :return: Returns a list of messages (dictionaries) from the parsed threads.
    """

    filenames = os.listdir(location)
    messages = []

    print("Parsing files in {}".format(location))

    for file in filenames:
        threadid = file.split('.')[1].split('.')[0]

        with open(os.path.join(location, file), encoding='utf-8') as threadfile:
            soup = BeautifulSoup(threadfile, 'lxml')

            for element in soup.find_all('message'):

                postid = element.postid.get_text()
                username = element.username.get_text()
                text = element.find('text').text

                date = element.date.get_text()
                if 'Edited: ' in date:
                    date = date.replace('Edited: ', '')
                date = dateutil.parser.parse(date)
                date = date.isoformat()

                messagedict = {
                    "postid": int(postid),
                    "threadid": int(threadid),
                    # "username": username,
                    # "date": date,
                    "text": text
                }

                messages.append(messagedict)

    print("Parsed {} messages.".format(len(messages)))
    return messages

def labelparser(filename):

    with open(filename, encoding='utf-8') as csvfile:
        labeldatareader = csv.DictReader(csvfile, fieldnames=["threadid", "postid", "bookid"], delimiter='\t')
        labeldata = [d for d in labeldatareader]

    return labeldata

def metaparser(filename):

    d = dict()

    with open(filename, encoding='utf-8') as jsonfile:
        metadata = jsonfile.readlines()

        print(metadata[0])

        for bookmeta in metadata:
            meta = json.loads(bookmeta)
            d[meta["workID"]] = meta["versions"]

    return d

def bookmatcher(message, labeldata):
    """
    Finds bookid for each message (training).
    :param message:
    :return: bookid(int)
    """

    threadid = message['threadid']
    postid = message['postid']

    bookids = tuple(d['bookid'] for d in labeldata if int(d['postid']) == postid and int(d['threadid']) == threadid)

    return bookids

def labeler(data, labeldata):
    y = []

    for message in data:
        bookids = bookmatcher(message, labeldata)

        if bookids == []:
            bookids = ("UNKNOWN",)
        y.append(bookids)

    return y

def titlelist(metadata):
    """
    Return list of titles from meta data
    :param meta:
    :return:
    """
    all_titles = []

    for workid, versions in metadata.items():     
        for version in versions:
            booktitle = version["booktitle"]
            all_titles.append(booktitle)
            
    return set(all_titles)


def build_titlelist(metadata, d):
    """
    Return list of titles from meta data. Titles are stored under their corresponding word keys. 
    This for faster matching using the Levenstheins distance. 
    :param meta:
    :return:
    """
    
    for workid, versions in metadata.items():
        for version in versions:
            booktitle = version["booktitle"]
            author = version["author"]
            
            booktitle = re.sub('\(.*\)', '', booktitle)   
            booktitle = booktitle.strip()

            tokens = list(set(word_tokenize(booktitle.lower())))
            
            for word in tokens:
                try:
                    d[word].add((booktitle, author, workid))
                except:
                    d[word] ={(booktitle, author, workid)}
                    
                    
    return d

def clean_booktitle(booktitle):

    booktitle = re.sub('\(.*\)', '', booktitle)   
    booktitle = booktitle.strip()
    
    return booktitle


if __name__ == "__main__":

    # Parse metadata
    # metadict = metaparser(METAFILE)

    with open('data/titles.pickle', 'rb') as picklefile:
        d = pickle.load(picklefile)

    # Parse messages from the .xml files
    training_data = threadparser(TRAINFOLDER)
    # test_data = threadparser(TESTFOLDER)

    # Training class data (bookids to messages)
    labeldata_train = labelparser(LABELFILETRAIN)
    # labeldata_test = labelparser(LABELFILETEST)

    trainkeys = [i["bookid"] for i in labeldata_train]
    # testkeys = [i["bookid"] for i in labeldata_test]





