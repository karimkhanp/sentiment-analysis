from __future__ import division
from math import log, exp
from operator import mul
from collections import Counter
import os
import pylab, gearman, json
import cPickle

pos = dict()
neg = dict()
features = set()
totals = [0, 0]
delchars = ''.join(c for c in map(chr, range(128)) if not c.isalnum())

CDATA_FILE = "countdata.pickle"

class MyDict(dict):
    def __getitem__(self, key):
        if key in self:
            return self.get(key)
        return 0
    
    def __init__(self):
        self.train()
        print "Trained..."
        self.gearman_worker = gearman.GearmanWorker( ['localhost:4730'] )
        self.gearman_worker.register_task('call_sentiment_worker', self.classify_demo)

    def negate_sequence(self,text):
        """
        Detects negations and transforms negated words into "not_" form.
        """
        negation = False
        delims = "?.,!:;"
        result = []
        words = text.split()
        prev = None
        pprev = None
        for word in words:
            # stripped = word.strip(delchars)
            stripped = word.strip(delims).lower()
            negated = "not_" + stripped if negation else stripped
            result.append(negated)
            if prev:
                bigram = prev + " " + negated
                result.append(bigram)
                if pprev:
                    trigram = pprev + " " + bigram
                    result.append(trigram)
                pprev = prev
            prev = negated
    
            if any(neg in word for neg in ["not", "n't", "no"]):
                negation = not negation
    
            if any(c in word for c in delims):
                negation = False
    
        return result
    
    
    def train(self):
        global pos, neg, totals
        retrain = False
        
        # Load counts if they already exist.
        if not retrain and os.path.isfile(CDATA_FILE):
            pos, neg, totals = cPickle.load(open(CDATA_FILE))
            return

    def classify_demo(self, gearman_worker, gearman_job):
        final_result = {}
        print "Classification started"
        data = json.loads(gearman_job.data)
        text = data["text"]
        print "Received data :", text        
        words = set(word for word in self.negate_sequence(text) if word in pos or word in neg)
        if (len(words) == 0): 
            print "No features to compare on"
            return True
    
        pprob, nprob = 0, 0
        # print "\nResult with log"
        
        for word in words:
            pp = (pos[word] + 1) / (2 * totals[0])
            np = (neg[word] + 1) / (2 * totals[1])
            #print "%15s %.9f %.9f" % (word, exp(pp), exp(np))
            pprob += pp
            nprob += np
        p = (pprob/(pprob + nprob))*100
        n = (nprob/(pprob + nprob))*100
        final_result['pos'] = p
        final_result['neg'] = n
        print "Positive : ", p
        print "Negative : ", n
        return json.dumps(final_result)
    
    def prune_features(self):
        """
        Remove features that appear only once.
        """
        global pos, neg
        for k in pos.keys():
            if pos[k] <= 1 and neg[k] <= 1:
                del pos[k]
    
        for k in neg.keys():
            if neg[k] <= 1 and pos[k] <= 1:
                del neg[k]

if __name__ == '__main__':
    MyDict().gearman_worker.work()
    # MyDict().train()
    # while True:
    #     text = raw_input("Please enter the sentence : ")
    #     MyDict().classify_demo(text)
