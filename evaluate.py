import csv
from collections import defaultdict

GOLDFILE = 'results/sbs16mining-linking-test-labels-librarything.csv'
RESULTS = 'results/results_np.csv'

def reader(file):

    with open(file, 'r', encoding='utf-8') as goldfile:
        d = defaultdict(list)

        values = goldfile.read().split('\n')

        for v in values:
            if v:
                threadid, postid, workid = v.split('\t')

            d[(threadid, postid)].append(workid)

    return d


def precision(golddict, resultsdict):
    TP = 0
    FP = 0

    for k, v in golddict.items():
        for workid in v:
            if workid in resultsdict[k]:
                TP += 1

    for k, v in resultsdict.items():
        for workid in v:
            if workid not in golddict[k]:
                FP += 1

    return TP / (TP + FP)


def recall(golddict, resultsdict):
    TP = 0
    FN = 0

    for k, v in golddict.items():
        for workid in v:
            if workid in resultsdict[k]:
                TP += 1

    for k, v in golddict.items():
        for workid in v:
            if workid not in resultsdict[k]:
                FN += 1

    return TP / (TP + FN)


def f_score(precision, recall):

    return 2 * (precision * recall) / (precision + recall)


def dict_equalizer(golddict, resultsdict):
    """
    The calculations should only be done on messages
    that are in both files (gold and resultsrun),
    otherwise this would influence the overal counts.

    This function makes shure both dictionaries have the same keys.  
    """

    goldset = set(golddict)
    resultset = set(resultsdict)

    non_equal = goldset.difference(resultset)
    non_equal.update(resultset.difference(goldset))

    for item in non_equal:
        
        if item in golddict:
            del golddict[item]

        if item in resultsdict:
            del resultsdict[item]

    return golddict, resultsdict

def metrics(GOLDFILE, RESULTS):

    golddict = reader(GOLDFILE)
    resultsdict = reader(RESULTS)

    golddict, resultsdict = dict_equalizer(golddict, resultsdict)

    print(len(golddict))
    print(len(resultsdict))

    P = precision(golddict, resultsdict)
    R = recall(golddict, resultsdict)
    f_measure = f_score(P, R)

    return P, R, f_measure

if __name__ == "__main__":


    print(metrics(GOLDFILE, RESULTS))
    

