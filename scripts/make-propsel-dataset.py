#!/usr/bin/python3

import json
from nltk.tokenize import word_tokenize
import csv
import sys

PROP_SEP = " # "
ENT_TOK = "ENT_TOK"

replace = int(sys.argv[1])
split = sys.argv[2]
dataset_dir = sys.argv[3]
out_file = sys.argv[4]

all_paths_file = dataset_dir + "/d-relation-dump/" + split + ".json"
gold_standard_file = dataset_dir + "/d-freebase-brp-reduced/" + split + ".json"
main_file = dataset_dir + "/main/" + split + ".json"
dump_file = dataset_dir + "/d-dump/" + split + ".json"
mid_file = dataset_dir + "/d-freebase-mids/" + split + ".json"

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

mids = {}       
with open(mid_file) as f:
    jsobj = json.load(f)
    for line in jsobj:
        for m in line['freebaseMids']:
            try:
                mids[m['pageID']] = m['mid']
            except KeyError:
                pass

out = open(out_file, 'w')
outcsv = csv.DictWriter(out, fieldnames=['qtext', 'label', 'atext'])
outcsv.writeheader()

for line in gold:
    gs_path_list = [tuple(prop[1:].replace("/",".") for prop in path[0]) for path in line['relPaths']]
    all_paths = [tuple(prop['property'] for prop in path['path']) for path in all_map[line['qId']]]
    all_paths_labels = [tuple(prop['label'] for prop in path['path']) for path in all_map[line['qId']]]
    entities = [tuple(path['entities']) for path in all_map[line['qId']]]

    qtext = main[line['qId']].lower()
    if (qtext[-1] != "?"):
        if (qtext[-1] == ' '):
            qtext = qtext + "?"
        else:
            qtext = qtext + " ?"
    elif (qtext[-2] != ' '):
        qtext = qtext[:-1] + " ?" 
    
    concepts = dump[line['qId']]

    print(qtext)
    for e, path, path_labels in zip(entities, all_paths, all_paths_labels):
        ent_mids = [em[1:].replace('/','.') for em in e]
        idxs = []
        qtext_new = qtext
        if (replace == 1):
            for c in concepts:
                try:
                    if (mids[c['pageID']] in ent_mids):
                        idxs.append((c['begin'], c['end']))
                except KeyError:
                    pass
            idxs = list(set(idxs))
            idxs.sort()
            for b,e in reversed(idxs):
                qtext_new = qtext_new[:b] + ENT_TOK + qtext_new[e:]
        # print(qtext_new)        
        # print(e, [c['pageID'] for c in concepts])
        # num = 2
        # try:
        #     gs_path_list2 = [g[num] for g in gs_path_list]
        #     # print(path, gs_path_list2)
        #     if (path[num] in gs_path_list2):
        #         y = 1
        #     else:
        #         y = 0
        # except IndexError:
        #     y = 0
        filtered = False
        if (path in gs_path_list):
            y = 1
        else:
            y = 0
            for p in path:
                if ('common.' in p or 'type.' in p):
                    filtered = True
                    break
        if (filtered):
            continue
        tokenized = [' '.join(word_tokenize(lab.lower())) for lab in path_labels]
        labels_csv = PROP_SEP.join(tokenized)
        try:
            # labels_csv = tokenized[num]
            outcsv.writerow({'qtext':qtext_new, 'label':y, 'atext':labels_csv})
        except IndexError:
            pass
    # break

out.close()
