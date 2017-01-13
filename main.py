import os
import csv
import json
import dateutil.parser
from collections import defaultdict
from bs4 import BeautifulSoup

TRAINFOLDER = 'data/train/'
LABELFILE = 'data/sbs16mining-linking-training-labels.csv'
METAFILE = 'data/sbs16mining.book-metadata.json'
TESTFOLDER = 'data/test/'

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

    for file in filenames:
        threadid = file.split('.')[1].split('.')[0]

        with open(os.path.join(location, file), encoding='utf-8') as threadfile:
            soup = BeautifulSoup(threadfile, 'lxml')

            for element in soup.find_all('message'):

                postid = element.postid.get_text()
                username = element.username.get_text()
                text = element.text

                date = element.date.get_text()
                if 'Edited: ' in date:
                    date = date.replace('Edited: ', '')
                date = dateutil.parser.parse(date)

                messagedict = {
                    "postid": int(postid),
                    "threadid": int(threadid),
                    "username": username,
                    "date": date,
                    "text": text
                }

                messages.append(messagedict)

    return messages

def labelparser(filename):

    with open(filename, encoding='utf-8') as csvfile:
        labeldatareader = csv.DictReader(csvfile, fieldnames=["threadid", "postid", "bookid"], delimiter='\t')
        labeldata = [d for d in labeldatareader]

    return labeldata

def metaparser(filename):

    meta = json.load(filename)

def bookmatcher(message, labeldata):
    """
    Finds bookid for each message (training).
    :param message:
    :return: bookid(int)
    """

    threadid = message['threadid']
    postid = message['postid']

    bookid = [d['bookid'] for d in labeldata if d['postid'] == postid and d['threadid'] == threadid][0]

    return bookid


if __name__ == "__main__":

    print(threadparser('data/train/'))
    # labeldata = labelparser('data/sbs16mining-linking-training-labels.csv')
    # print(bookmatcher(message, labeldata))
    #
    # metaparser('sbs16mining.book-metadata.json')
