#!/usr/bin/env python

from optparse import OptionParser
import os, logging
import collections, math, re

def preprocess(line):
    line = line.lower()
    pattern = re.compile(r'[a-z|A-Z]+')
    line = ' '.join(pattern.findall(line))
    return line

def calc_probability(filepath, model):
    trigrams = model[0]
    bigrams = model[1]
    probability = 0
    f = open(filepath, 'r')
    for l in f.readlines():
        l = preprocess(l)
        for t in l.split(' '):
            t = '$$'+t+'$$'
            for i in range(len(t)):
                if i < len(t) - 2:
                    bg = bigrams[t[i]][t[i+1]]
                    tg = trigrams[t[i]][t[i+1]][t[i+2]]
                    probability += math.log(tg + 1.0) - math.log(bg + 26*26.0)

    return probability

def create_model(path):
    model = None
    
    bigrams = collections.defaultdict(lambda: collections.defaultdict(int))
    trigrams = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(int)))

    f = open(path, 'r')
    for l in f.readlines():
        l = preprocess(l)
        for t in l.split(' '):
            t = '$$'+t+'$$'
            for i in range(len(t)):
                if i < len(t) - 1: bigrams[t[i]][t[i+1]] += 1
                if i < len(t) - 2: trigrams[t[i]][t[i+1]][t[i+2]] += 1

    return trigrams, bigrams

def predict(file, model_en, model_es):
    prediction = None

    p_en = calc_probability(file, model_en)
    p_es = calc_probability(file, model_es)
    if p_en > p_es : 
        prediction = "English"
    else : 
        prediction = "Spanish"
    return prediction

def main(en_tr, es_tr, folder_te):
    ## STEP 1: create a model for English with file en_tr
    model_en = create_model(en_tr)

    ## STEP 2: create a model for Spanish with file es_tr
    model_es = create_model(es_tr)

    ## STEP 3: loop through all the files in folder_te and print prediction
    folder = os.path.join(folder_te, "en")
    print "\nPrediction for English documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))
    
    folder = os.path.join(folder_te, "es")
    print "\nPrediction for Spanish documents in test:"
    for f in os.listdir(folder):
        f_path =  os.path.join(folder, f)
        print "%s\t%s" % (f, predict(f_path, model_en, model_es))

if __name__ == "__main__":
    usage = "usage: %prog [options] EN_TR ES_TR FOLDER_TE"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug", action="store_true",
                      help="turn on debug mode")

    (options, args) = parser.parse_args()
    if len(args) != 3:
        parser.error("Please provide required arguments")

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.CRITICAL)

    main(args[0], args[1], args[2])
