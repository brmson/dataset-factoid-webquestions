#!/usr/bin/python
#
# rawimport.py - generate git-stored data from raw datasets as used in SEMPRE
#
# Example: rawimport.py raw/ main/ d-freebase/

from __future__ import print_function
import json
import re
import sys

import datalib

# N.B. these proportions should be equal or commensurable, see resplit_train()
PROP_DEVTEST = 0.05  # proportional size of devtest split
PROP_VAL = 0.2  # proportional size of val split


def targetsToAnswers(target):
    """ Convert raw's targetValue lambda-form to a plain list of answer strings. """
    # (list (description "Jazmyn Bieber") (description "Jaxon Bieber"))
    target = re.sub(r'^\(list |\)$', '', target)
    for answers in re.findall(r'\(description (?:"([^"]+?)"|([^)]+?))\) *', target):
        for answer in answers:
            if answer:
                yield answer


def questions_pproc(questions, ch):
    """ Post-process raw json data, outputting main and freebase-specific data sets. """
    qs_main = []
    qs_fb = []
    for i, q in enumerate(questions):
        q_main = {'qId': 'wq%c%06d' % (ch, i),
                  'qText': q['utterance'],
                  'answers': list(targetsToAnswers(q['targetValue']))}
        q_fb = {'qId': q_main['qId'],
                'freebaseKey': q['url'].replace('http://www.freebase.com/view/en/', '')}
        qs_main.append(q_main)
        qs_fb.append(q_fb)
    return qs_main, qs_fb


def resplit_train(data):
    """ re-split train split, returning a tuple of the three new splits """
    # In order to produce a deterministic train re-split with growing dataset
    # and thanks to the fact that re-split proportions are commensurable, for
    # proportion p of k-th new split, we take every (k + 1/p)-th question.
    devtest = []
    val = []
    trainmodel = []
    for i, q in enumerate(data):
        if (i+0) % (1/PROP_DEVTEST) == 0:
            devtest.append(q)
        elif (i+1) % (1/PROP_VAL) == 0:
            val.append(q)
        else:
            trainmodel.append(q)
    return devtest, val, trainmodel


def save_data(split, maindir, questions_main, fbdir, questions_fb):
    """ save full dataset for a given split """
    for data, fname in [(questions_main, '%s/%s.json' % (maindir, split)), (questions_fb, '%s/%s.json' % (fbdir, split))]:
        with open(fname, 'w') as f:
            datalib.save_json(data, f)


if __name__ == "__main__":
    rawdir, maindir, fbdir = sys.argv[1:]

    for split, ch in [('train', 'r'), ('test', 's')]:
        with open('%s/webquestions.examples.%s.json' % (rawdir, split)) as f:
            questions = json.load(f)

        questions_main, questions_fb = questions_pproc(questions, ch)

        if split == "train":
            # Build some extra splits
            devtest_main, val_main, trainmodel_main = resplit_train(questions_main)
            devtest_fb, val_fb, trainmodel_fb = resplit_train(questions_fb)
            for nsplit, nsplit_main, nsplit_fb in [
                    ('devtest', devtest_main, devtest_fb),
                    ('val', val_main, val_fb),
                    ('trainmodel', trainmodel_main, trainmodel_fb)]:
                save_data(nsplit, maindir, nsplit_main, fbdir, nsplit_fb)

        else:
            save_data(split, maindir, questions_main, fbdir, questions_fb)
