#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import utils
import collections
import math
import time
import operator

def create_model(sentences):
    wordtagbi = collections.defaultdict(lambda: collections.defaultdict(int))
    for sentence in sentences:
        for token in sentence:
            wordtagbi[token.word][token.tag] += 1
    for c1,r1 in wordtagbi.items():
        for c2,r2 in r1.items():
            wordtagbi[c1][c2] = math.log1p(r2)
    return wordtagbi

def predict_tags(sentences, wordtagbi):
    for sentence in sentences:
        for token in sentence:
            tag = "NN"
            if wordtagbi.has_key(token.word):
                tag = max(wordtagbi[token.word].iteritems(), key=operator.itemgetter(1))[0]
            token.tag = tag
    return sentences

if __name__ == "__main__":
    usage = "usage: %prog [options] GOLD TEST"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 2:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    training_file = args[0]
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    test_sents = utils.read_tokens(test_file)

    model = create_model(training_sents)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    predictions = predict_tags(sents, model)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)
