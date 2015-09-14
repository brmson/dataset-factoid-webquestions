#!/usr/bin/python -u

from __future__ import print_function
import sys, json
from urllib2 import urlopen

apikey = "AIzaSyAJb3Ze9JAmFBqaxd4U9R4MQLXL6MbjSZI"

def walk_node(node, pathprefix, labels):
    relpaths = []
    for name, val in node['property'].items():
        for value in val['values']:
            if value['text'] in labels:
                relpaths.append(tuple(pathprefix + [name]))
            if 'property' in value:
                relpaths += walk_node(value, pathprefix + [name], labels)
    return relpaths

def save_json(data, f):
    """ save data in a given file as json, one line per data item """
    print('[', file=f)
    for q in data:
        e = ',' if q != data[-1] else ''
        print(' ' + json.dumps(q) + e, file=f)
    print(']', file=f)

with open(sys.argv[1]) as f:
    dataset = json.load(f)
    
with open(sys.argv[2]) as f:
    dump = json.load(f)

with open(sys.argv[3]) as f:
    keys = json.load(f)


concept_paths = dict()
for i, line in enumerate(dataset):
    id = line['qId']
    concepts = [concept['fullLabel'] for concept in dump[i]['Concept']]
    key = keys[i]['freebaseKey']    
    url = 'https://www.googleapis.com/freebase/v1/topic/en/' + key
    urlresp = urlopen(url + '?key=' + apikey)
    resp = json.loads(urlresp.read().decode('utf-8'))
    concept_paths[id] = walk_node(resp, [], concepts)

new_paths = {}
for line in dataset:
    key = line['qId']
    paths = list(set([tuple(path[0]) for path in line['relPaths']]))
    concept_path = list(set(concept_paths[key]))
    for p in paths:        
        if (len(p) < 2):
            continue
        for path in concept_path:            
            if len(path) < 2:
                continue
            flag = False
            for node in path:
                if node in p:
                    flag = True            
            if flag:                 
                new_paths[key] = path
   

for line in dataset:
    new = new_paths[line['qId']]
    for i, p in enumerate(line['relPaths']):
        if new[0] in p[0]:  
            line['relPaths'][i][0].append(new[1])

    
with open("pokus.json", "w") as f:
    save_json(dataset, f)