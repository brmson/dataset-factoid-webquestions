#!/usr/bin/python -u
# Resplit main/train.json to the three sub-splits.

from collections import OrderedDict

import datalib
from rawimport import resplit_train


if __name__ == "__main__":
    questions_main = datalib.load_multi_data('train', ['main'])

    qlist_wqr = []
    qlist_mfb = []
    for q in questions_main.to_list():
        q2 = OrderedDict([('qId', q['qId']), ('answers', q['answers']), ('qText', q['qText'])])
        if q['qId'].startswith('wqr'):
            qlist_wqr.append(q2)
        else:
            qlist_mfb.append(q2)
    qlist = qlist_wqr + qlist_mfb

    devtest_main, val_main, trainmodel_main = resplit_train(qlist)
    for nsplit, nsplit_main in [
            ('devtest', devtest_main),
            ('val', val_main),
            ('trainmodel', trainmodel_main)]:
        with open('main/%s.json' % (nsplit,), 'w') as f:
            datalib.save_json(nsplit_main, f, sort_keys=False)
