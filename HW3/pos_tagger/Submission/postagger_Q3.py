#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import utils
import collections
import math
import time
import operator

def create_model(sentences):
    taguni = collections.defaultdict(int)
    tagtagbi = collections.defaultdict(lambda: collections.defaultdict(int))
    wordtagbi = collections.defaultdict(lambda: collections.defaultdict(int))
    for sentence in sentences:
        prevtag = "<s>"
        for token in sentence:
            taguni[token.tag] += 1
            tagtagbi[token.tag][prevtag] += 1
            wordtagbi[token.word.lower()][token.tag] += 1
            prevtag = token.tag
    taguni["<s>"] = len(sentences)
    for currTag, prevTagSet in tagtagbi.items():
        for prevTag, value in prevTagSet.items():
            tagtagbi[currTag][prevTag] = math.log1p(value + 1.0) - math.log1p(taguni[prevTag] + 45.0)
    for word, tagset in wordtagbi.items():
        for tag, value in tagset.items():
            wordtagbi[word][tag] = math.log1p(value)
    return tagtagbi, wordtagbi, taguni

def predict_tags(sentences, model):
    tagtagbi = model[0]
    wordtagbi = model[1]
    taguni = model[2]
    for sentence in sentences:
        viterbi = collections.defaultdict(lambda: collections.defaultdict(int))
        for t in range(len(sentence)):
            token = sentence[t]
            if not wordtagbi.has_key(token.word.lower()):
                tag = getTag(token.word)
                setViterbi(t, tag, tagtagbi, taguni, viterbi, math.log1p(1.0))
            else:
                for tag, unusedValue in taguni.items():
                    if tag != "<s>":
                        if wordtagbi[token.word.lower()].has_key(tag):
                            wtbv = wordtagbi[token.word.lower()][tag]
                        else:
                            wtbv = math.log1p(1.0) - math.log1p( taguni[tag] + 45.0 )
                        setViterbi(t, tag, tagtagbi, taguni, viterbi, wtbv)
        maxitem = (0.0, "")
        i = len(viterbi) - 1
        while i > -1:
            if i == len(viterbi) - 1:
                #selectedtag, prevItem = max(viterbi[i].iteritems(), key=operator.itemgetter(1))
                selectedtag = ""
                mv = 0
                for key, val in viterbi[i].items():
                    if selectedtag == "" or val[0] > mv:
                        selectedtag = key
                        mv = val[0]
                        maxitem = val
                sentence[i].tag = selectedtag
            else:
                try:
                    sentence[i].tag = maxitem[1]
                    maxitem = viterbi[i][maxitem[1]]
                except:
                    print sentence[i].word + " " + sentence[i].tag
            i -= 1
    return sentences

def getTag(word):
    tag = "NNP"
    if word.isupper(): return tag
    w = word.lower()
    if w[0].isdigit():
        tag = "CD"
        if (any(c.isalpha() for c in w)):
            tag = "JJ"
    elif w.startswith("anti-"): tag = "JJ"
    elif w.startswith("well"): tag = "JJ"
    elif w.startswith("then-"): tag = "JJ"
    elif w.startswith("three-"): tag = "JJ"
    elif "tax-" in w: tag = "JJ"
    elif "-tax" in w: tag = "JJ"
    elif w in ["ahs","ah","amen","hee","oohs","uh-uh","yeah"]: tag = "UH"
    elif w in ["t34c","Thirty-five","Twenty-four"]: tag = "CD"
    elif w in ["'cause", "astride", "nearer"]: tag = "IN"
    elif w in ["wherein"]: tag = "WRB"
    elif w in [ ".what"]: tag = "WDT"
    return tag

def setViterbi(t, tag, tagtagbi, taguni, viterbi, wtbv):
    if t == 0:
        if tagtagbi[tag]["<s>"] == 0:
            tagtagbi[tag]["<s>"] = math.log1p(1.0) - math.log1p(taguni["<s>"] + 45.0)
        viterbi[t][tag] = wtbv + tagtagbi[tag]["<s>"], "<s>"
    else:
        #values = []
        maxval = 0
        pTag = ""
        for prevTag, val in viterbi[t - 1].items():
            if tagtagbi[tag][prevTag] == 0: tagtagbi[tag][prevTag] = math.log1p(1.0) - math.log1p(
                taguni[prevTag] + 45.0)

            vit = val[0] + wtbv + tagtagbi[tag][prevTag]
            if pTag == "" or vit > maxval:
                pTag = prevTag
                maxval = vit
            #values.append((vit, prevTag))
        #viterbi[t][tag] = max(values, key=lambda x: x[0])
        viterbi[t][tag] = (maxval, pTag)


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
    #training_file = 'data_public/hw3_train'
    training_sents = utils.read_tokens(training_file)
    test_file = args[1]
    #test_file = 'data_public/hw3_heldout_aa'
    test_sents = utils.read_tokens(test_file)

    start_time = time.time()
    model = create_model(training_sents)
    end_time = time.time()
    print "Elapsed time for Creating Model was %g seconds" % (end_time - start_time)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(test_file)
    start_time = time.time()
    predictions = predict_tags(sents, model)
    end_time = time.time()
    print "Elapsed time for Calculating Accuracy was %g seconds" % (end_time - start_time)
    accuracy = utils.calc_accuracy(test_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)

    ## read sentences again because predict_tags(...) rewrites the tags
    sents = utils.read_tokens(training_file)
    start_time = time.time()
    predictions = predict_tags(sents, model)
    end_time = time.time()
    print "Elapsed time for Calculating Accuracy was %g seconds" % (end_time - start_time)
    accuracy = utils.calc_accuracy(training_sents, predictions)
    print "Accuracy in training [%s sentences]: %s" % (len(sents), accuracy)
