#!/usr/bin/python3

import json
from nltk.tokenize import word_tokenize
import csv
import sys

LIMIT = int(sys.argv[1])
split = sys.argv[2]
dataset_dir = sys.argv[3]
out_file = sys.argv[4]

all_paths_file = dataset_dir + "/d-relation-dump/" + split + ".json"
gold_standard_file = dataset_dir + "/d-freebase-brp/" + split + ".json"
main_file = dataset_dir + "/main/" + split + ".json"
dump_file = dataset_dir + "/d-dump/" + split + ".json"

with open(gold_standard_file) as f:
    gold = json.load(f)
    
all_map = {}
with open(all_paths_file) as f:
    jsobj = json.load(f)
    for line in jsobj:
        all_map[line['qId']] = line['exploringPaths']
main = {}        
with open(main_file) as f:
    jsobj = json.load(f)
    for line in jsobj:
        main[line['qId']] = line['qText']
dump = {}       
with open(dump_file) as f:
    jsobj = json.load(f)
    for line in jsobj:
        dump[line['qId']] = line['Concept']

out = open(out_file, 'w')
outcsv = csv.DictWriter(out, fieldnames=['qtext', 'label', 'atext'])
outcsv.writeheader()

for line in gold:
    gs_path_list = [tuple(prop[1:].replace("/",".") for prop in path[0]) for path in line['relPaths']]
    all_paths = [tuple(prop['property'] for prop in path) for path in all_map[line['qId']]]
    all_paths_labels = [tuple(prop['label'] for prop in path) for path in all_map[line['qId']]]

    qtext = main[line['qId']].lower().replace("?","")
    idxs = []
    concepts = dump[line['qId']]
    concepts.sort(key = lambda x: x['score'], reverse = True)
    for concept in concepts[:LIMIT]:
        idxs.append((concept['begin'], concept['end']))
    idxs = list(set(idxs))
    idxs.sort()
    for b,e in reversed(idxs):
        qtext = qtext[:b] + "<e>" + qtext[e:]
    print(qtext)
    for path, path_labels in zip(all_paths, all_paths_labels):
        if (path in gs_path_list):
            y = 1
        else:
            y = 0
        tokenized = [' '.join(word_tokenize(lab.lower())) for lab in path_labels]
        labels_csv = ' ### '.join(tokenized)
        outcsv.writerow({'qtext':qtext, 'label':y, 'atext':labels_csv})

out.close()