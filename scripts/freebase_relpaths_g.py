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


def cMid(c):
    """ return mid of concept as stored in freebaseMids json """
    return c['mid'].split('.')[1] if c['mid'] != '' else None


def walk_node(node, pathprefix, pathsuffixes, labels, other_c):
    relpaths = []

    pathsuffixes = list(pathsuffixes)  # local copy
    if other_c is not None and pathprefix:
        # Try branching out in the middle node.
        for name, val in node['property'].items():
            for value in val['values']:
                if 'id' in value and value['id'][3:] in [cMid(c) for c in other_c]:
                    # First, go for an exact match.
                    # id[3:] -> split leading /m/ in the mid
                    pathsuffixes += [name + '!']

                else:
                    # Substring label match.
                    for c in other_c:
                        if c['concept'] in value['text']:
                            pathsuffixes += [name + '~']

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
                relpaths += walk_node(value, pathprefix + [name], pathsuffixes, labels, other_c)

    return relpaths


def get_mid_rp(q, mid, other_c):
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

    path_labels = walk_node(resp, [], [], set(q['answers']), other_c)
    return path_labels


def get_question_rp(q):
    print('>> %s %s' % (q['qId'], q['qText']))
    path_labels = []
    for c in q['freebaseMids']:
        mid = cMid(c)
        if mid is None:
            continue

        global mode
        if mode == 'brp':
            other_c = [cc for cc in q['freebaseMids'] if cc != c]
        else:
            other_c = None
        path_labels += get_mid_rp(q, mid, other_c)

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
