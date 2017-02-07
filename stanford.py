# ## Stanford Parsers

import os
from nltk.tag import StanfordNERTagger
from nltk.parse.stanford import StanfordParser
from nltk.tokenize import sent_tokenize

os.environ['JAVAHOME'] = 'C:\\Program Files\\Java\\jre1.8.0_77'
os.environ['CLASSPATH'] = "C:/Users/Leon/Dropbox/VU/5.3_LOT_Text_Mining/stanford-ner-2016-10-31/"


def constituencyparser(sequence):
    
    parser = StanfordParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
      
    sentences = sent_tokenize(sequence)
    parse = parser.raw_parse_sents(sentences)
    
    trees = list(parse)
    
    return trees


def NERtagger(text):
    
    sequence = word_tokenize(text)

    parser = StanfordNERTagger('C:/Users/Leon/Dropbox/VU/5.3_LOT_Text_Mining/stanford-ner-2016-10-31/classifiers/english.all.3class.distsim.crf.ser.gz')
    # parser = stanford.StanfordParser(model_path="stanford-corenlp-full-2016-10-31/englishPCFG.ser.gz")

    return parser.tag(sequence)
