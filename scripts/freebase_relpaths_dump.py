#!/usr/bin/python3
#
# Find Freebase relation path between concept URL and answer for each question
#
# Use the Google API for Freebase mtaching answers in the subgraph of the
# question concept, storing all relations that do lead to one.
#
# Example:
#   for split in devtest val trainmodel test; do echo $split; ./freebase_relpaths_dump.py $split $googleapikey; done
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
    return c['mid'].split('.')[1] if c['mid'] is not None and c['mid'] != '' else None

def is_filtered(property):
    filters = ['/type', '/common']
    filters = []
    for f in filters:
        if property.startswith(f):
            return True
    return False

def remove_duplicates(entity_paths):
    myset = set()
    res = []
    global answers
    if (answers == '1'):
        return entity_paths 
    for ent_path in entity_paths:
        # print(ent_path['path'])
        if (ent_path['path'] not in myset):
            myset.add(ent_path['path'])
            res.append(ent_path)  
    return res



def walk_node(node, ent_tops, ent_wits, pathprefix, pathsuffixes, other_c):
    relpaths = []
    global answers
    pathsuffixes = list(pathsuffixes)  # local copy
    if other_c is not None and pathprefix:
        # Try branching out in the middle node.
        for name, val in node['property'].items():
            if (is_filtered(name)):
                continue
            for value in val['values']:
                if 'id' in value and value['id'][3:] in [cMid(c) for c in other_c]:
                    # First, go for an exact match.
                    # id[3:] -> split leading /m/ in the mid
                    pathsuffixes += [name]
                    ent_wits += [value['id']]
                else:
                    # Substring label match.
                    for c in other_c:
                        if c['concept'] in value['text']:
                            pathsuffixes += [name]
                            ent_wits += [c['concept']]

    for name, val in node['property'].items():
        if (is_filtered(name)):
                continue
        for e, pathsuffix in zip(ent_wits, pathsuffixes):
            if (answers == '1'):
                relpaths.append({'entities': ent_tops + [e], 'path': tuple(pathprefix + [name, pathsuffix]), 'answers':[v['text'] for v in val['values']]})
            else:
                relpaths.append({'entities': ent_tops + [e], 'path': tuple(pathprefix + [name, pathsuffix])})
        if not pathsuffixes and ent_tops:
            if (answers == '1'):
                relpaths.append({'entities': ent_tops, 'path': tuple(pathprefix + [name]), 'answers':[v['text'] for v in val['values']]})
            else:
                relpaths.append({'entities': ent_tops, 'path': tuple(pathprefix + [name])})
        if not pathsuffixes and not ent_tops:
            if (answers == '1'):
                relpaths.append({'entities': [node['id']], 'path': tuple(pathprefix + [name]), 'answers':[v['text'] for v in val['values']]})
            else:
                relpaths.append({'entities': [node['id']], 'path': tuple(pathprefix + [name])})

    for name, val in node['property'].items():
        if (is_filtered(name)):
                continue
        for value in val['values']:
            if 'property' in value:
                relpaths += walk_node(value, ent_tops + [node['id']], ent_wits, pathprefix + [name], pathsuffixes, other_c)
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
            resp = json.loads(urlresp.read().decode('utf-8'))

            with open('fbconcepts/m.' + mid + '.json', 'w') as f:
                print(json.dumps(resp, indent=4), file=f)
        else:
            print("Warning!! Concept not found, skipping.")
            return []
            # raise e

    path_labels = walk_node(resp, [], [], [], [], other_c)
    return path_labels


def get_question_rp(q):
    print('>> %s %s' % (q['qId'], q['qText']))
    path_labels = []
    for c in q['freebaseMids']:
        mid = cMid(c)
        if mid is None:
            continue

        global mode
        other_c = [cc for cc in q['freebaseMids'] if cc != c]
        # Also try matching texts of plain clues
        other_c += [{'concept': cc['label'], 'mid': None} for cc in q['Clue']]

        path_labels += get_mid_rp(q, mid, other_c)

    # Count how many times each path occurs, sort by frequency
    # (to preserve run-by-run stability, secondary sort alphabetically)
    # pl_counter = Counter(path_labels)
    # pl_tuples = [(pl, c) for pl, c in pl_counter.items()]
    # pl_set = sorted(sorted(pl_tuples, key=itemgetter(0)), key=itemgetter(1), reverse=True)
    # pl_set = list(set(path_labels))
    pl_set = remove_duplicates(path_labels)
    return OrderedDict([('qId', q['qId']), ('exploringPaths', pl_set)])


if __name__ == "__main__":
    split = sys.argv[1]
    global mode
    global apikey
    global answers
    answers = sys.argv[2] if len(sys.argv) > 2 else None
    apikey = sys.argv[3] if len(sys.argv) > 3 else None
    data = datalib.load_multi_data(split, ['main', 'd-freebase-mids', 'd-dump'])

    # XXX: We would like to write the JSON file as we go, but we need
    # to test for last element in save_json() and things would just
    # get too complicated too needlessly.

    pool = Pool(processes=2)
    #qrp = pool.map(get_question_rp, data.to_list())
    qrp = map(get_question_rp, data.to_list())
    pool.close()
    pool.join()

    with open('d-relation-dump/%s_.json' % (split,), 'w') as f:
        datalib.save_json(list(qrp), f)
