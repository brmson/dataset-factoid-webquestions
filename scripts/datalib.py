""" a small library for the benefit of our python scripts """

from __future__ import print_function

import json


class QuestionSet(dict):
    """ a simple holder of questions; quacks like a dict, but can be
    easily dumped to a sorted list or offer other tools """

    def add(self, questions):
        """ add a list of questions """
        for q in questions:
            if q['qId'] in self:
                self[q['qId']].update(q)
            else:
                self[q['qId']] = q.copy()

    def to_list(self):
        return sorted(self.values(), key=lambda q: q['qId'])


def save_json(data, f):
    """ save data in a given file as json, one line per data item """
    print('[', file=f)
    for q in data:
        e = ',' if q != data[-1] else ''
        print(' ' + json.dumps(q) + e, file=f)
    print(']', file=f)
