#!/usr/bin/python3
#
# Find Freebase relation path between concept URL and answer for each question
#
# Use the Google API for Freebase mtaching answers in the subgraph of the
# question concept, storing all relations that do lead to one.
#
# Example:
#   for split in devtest val trainmodel test; do echo $split; ./freebase_relpaths_g.py $split rp $googleapikey; done
#
# The second argument is mode, either 'rp' or 'brp'; 'brp' stands for "branched"
# relation paths and in that case, occassionally the path will be of length 3
# (never occurs naturally in Freebase, apparently) and the last element will
# be a relation to a sibling of the answer property that leads to a co-occurring
# concept.
#
# If googleapikey is not passed, instead the script tries to read existing
# JSON freebase data dumps from the directory fbconcepts/ .

from __future__ import print_function

from collections import Counter, OrderedDict
import datalib
from multiprocessing import Pool
import json
from operator import itemgetter
import sys
from urllib.request import urlopen


def walk_node(node, pathprefix, pathsuffixes, labels, other_mids):
    relpaths = []

    pathsuffixes = list(pathsuffixes)  # local copy
    for name, val in node['property'].items():
        for value in val['values']:
            if other_mids is not None and pathprefix and 'id' in value and value['id'][3:] in other_mids:
                # other_mids not None? try branching out in the middle node
                # id[3:] -> split leading /m/ in the mid
                pathsuffixes += [name]

    for name, val in node['property'].items():
        for value in val['values']:
            if value['text'] in labels:
                for pathsuffix in pathsuffixes:
                    relpaths.append(tuple(pathprefix + [name, pathsuffix]))
                if not pathsuffixes:
                    relpaths.append(tuple(pathprefix + [name]))

    for name, val in node['property'].items():
        for value in val['values']:
            if 'property' in value:
                relpaths += walk_node(value, pathprefix + [name], pathsuffixes, labels, other_mids)

    return relpaths


def get_mid_rp(q, mid, other_mids):
    url = 'https://www.googleapis.com/freebase/v1/topic/m/' + mid

    global apikey
    try:
        with open('fbconcepts/m.' + mid + '.json', 'r') as f:
            resp = json.load(f)
    except FileNotFoundError as e:
        if apikey:
            # Download the data, not cached locally yet
            print(url)
            urlresp = urlopen(url + '?key=' + apikey)
            resp = json.loads(urlresp.readall().decode('utf-8'))

            with open('fbconcepts/m.' + mid + '.json', 'w') as f:
                print(json.dumps(resp, indent=4), file=f)
        else:
            raise e

    path_labels = walk_node(resp, [], [], set(q['answers']), set(other_mids) if other_mids is not None else None)
    return path_labels


def get_question_rp(q):
    print('>> %s %s' % (q['qId'], q['qText']))
    mids = [c['mid'].split('.')[1] for c in q['freebaseMids'] if c['mid'] != '']
    path_labels = []
    for mid in mids:
        global mode
        path_labels += get_mid_rp(q, mid, [m for m in mids if m != mid] if mode == 'brp' else None)

    # Count how many times each path occurs, sort by frequency
    # (to preserve run-by-run stability, secondary sort alphabetically)
    pl_counter = Counter(path_labels)
    pl_tuples = [(pl, c) for pl, c in pl_counter.items()]
    pl_set = sorted(sorted(pl_tuples, key=itemgetter(0)), key=itemgetter(1), reverse=True)

    return OrderedDict([('qId', q['qId']), ('relPaths', pl_set)])


if __name__ == "__main__":
    split = sys.argv[1]
    global mode
    mode = sys.argv[2]
    if not mode in ['rp', 'brp']:
        raise ValueError('unknown mode ' + mode)
    global apikey
    apikey = sys.argv[3] if len(sys.argv) > 3 else None
    data = datalib.load_multi_data(split, ['main', 'd-freebase-mids'])

    # XXX: We would like to write the JSON file as we go, but we need
    # to test for last element in save_json() and things would just
    # get too complicated too needlessly.

    pool = Pool(processes=2)
    #qrp = pool.map(get_question_rp, data.to_list())
    qrp = map(get_question_rp, data.to_list())
    pool.close()
    pool.join()

    with open('d-freebase-%s/%s.json' % (mode, split,), 'w') as f:
        datalib.save_json(list(qrp), f)
