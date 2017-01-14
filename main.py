import os
import csv
import json
import dateutil.parser
import numpy as np
from collections import defaultdict
from bs4 import BeautifulSoup
import logging as log
import pickle

from classification import *

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
                text = element.text

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
                    # "text": text
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

    meta = json.load(filename)



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

if __name__ == "__main__":

    # Parse messages from the .xml files
    training_data = threadparser(TRAINFOLDER)
    test_data = threadparser(TESTFOLDER)

    # Training class data (bookids to messages)
    labeldata_train = labelparser(LABELFILETRAIN)
    labeldata_test = labelparser(LABELFILETEST)
    
    trainkeys = [i["bookid"] for i in labeldata_train]
    testkeys = [i["bookid"] for i in labeldata_test]
    print(set(trainkeys).intersection(set(testkeys)))

    # Build y
    y = labeler(training_data, labeldata_train)
    #
    # metaparser('sbs16mining.book-metadata.json')

    print("Classify!")

    training_data = training_data
    test_data = test_data

    # Multi Label Classification
    mlb = MultiLabelBinarizer()
    yt = mlb.fit_transform(y)

    v = DictVectorizer(sparse=True)
    X = v.fit_transform(training_data)

    clf = OneVsRestClassifier(SVC(verbose=2))
    clf.fit(X, yt)

    with open('model.pickle', 'wb') as picklefile:
        pickle.dump(clf, picklefile)

    print()
    print("Predicting...")

    # v = DictVectorizer(sparse=False)
    X_test = v.transform(test_data)
    yt_test = clf.predict(X_test)

    yt_test = np.array(yt_test)
    y_test = mlb.inverse_transform(yt_test)
    # yt_test = np.expand_dims(yt_test, axis=0).transpose()
    # print(np.shape(yt_test))
    

    # print(mlb.inverse_transform(yt))
    # print(y)

    # print(y)
    # print(y_test)

    y_true = labeler(test_data, labeldata_test)
    y_true = mlb.transform(y_true)
    y_true = np.array(y_true)
    # y_true = np.expand_dims(y_true, axis=0).transpose()

    y_pred = yt_test
    # print(mlb.inverse_transform(y_true))



    print('true', y_true)
    print('pred', y_pred)

    f1 = f1_score(y_true, y_pred, average='samples')

    print("f1-score: {}".format(f1))