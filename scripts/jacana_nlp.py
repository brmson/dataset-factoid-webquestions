#!/usr/bin/python3
#
# Load Jacana's NLP preprocessing data, bind to IDs and store in d-entities/
#
# Example: jacana_nlp.py devtest webquestions.train.topics.json

from __future__ import print_function

import json
import sys
import datalib


def jacana_bind(data, jacanajson):
    """ bind jacana json by utterance texts to our dataset and get new prettier json """
    topicmap = dict([(jq['utterance'], jq['topics']) for jq in jacanajson])

    qnlp = []
    for q in data.to_list():
        topics = topicmap[q['qText']]
        topics = [topic.split(' ## ') for topic in topics]
        qnlp.append({'qId': q['qId'], 'entities': topics})
    return qnlp


if __name__ == "__main__":
    split, jacanafile = sys.argv[1:]

    data = datalib.load_multi_data(split, ['main'])

    with open(jacanafile, 'r') as jf:
        jacanajson = json.load(jf)

    qnlp = jacana_bind(data, jacanajson)

    with open('d-entities/%s.json' % (split,), 'w') as f:
        datalib.save_json(qnlp, f)
