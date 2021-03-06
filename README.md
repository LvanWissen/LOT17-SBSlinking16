# LOT17 Social Book Search Lab 2016
#### Mining track, task 2: linking

## Data
More information about the mining (linking) task at the [Social Book Search Lab website](http://social-book-search.humanities.uva.nl/#/mining) .

## Method

### Title candidates:
* Regex matching:
    Pattern: ‘Word stopwords* Word*’ (Capitalized words with stopwords (e.g. ‘in’, ‘the’) in between.   (Regular Expressions (regex) + stopword filtering)

* Sentence position
    A possible match is discarded if it is only one word and occurs the beginning of a sentence. (Tokenization)

* Parsing:	
    Filtering on constituency trees. We expect a title to be a NP. (Parsing)
	
* Author names: 
    Author names are added to the lookup if they occur within a window of 5 words around the matchphrase from the regex pattern. A possible match is discarded if it is a PERSON according to the Stanford NER Tokenizer. (NER)

### Classification mechanism

The title candidates and the surrounding authors are compared to a list of possible titles and authors. For the sake of speed and to compare only against titles resembling the candidate, the list is made by using a hashdict that consists of words as keys and titles containing this word as values. This way, the entire list of 2.758.660 titles from the metadata does not have to be used. We compute the Levenshtein distance between the candidate and all titles and keep the title and its workid with the highest score. Scores below 90% are discarded. 

### Evaluation

Evaluation is done by calculating the precision, recall and f-measure of the program’s run over the gold data. (F-Measure)

## How to use

```
    $ python main.py
```

Have a coffee, and another one... Then:


```
    $ python evaluate.py
```


## Results

|                   	| Precision 	| Recall 	| F-measure 	|
|-------------------	|-----------	|--------	|-----------	|
| Run1_NP_Selection 	| 0.297     	| 0.175  	| 0.220     	|
| Run2_without_NP   	| 0.240     	| 0.339  	| 0.281     	|


## Requirements

* fuzzywuzzy
* nltk
* Stanford CoreNLP and NER ([website](http://stanfordnlp.github.io/CoreNLP/))
* numpy
* beautifulsoup4
* python_dateutil



