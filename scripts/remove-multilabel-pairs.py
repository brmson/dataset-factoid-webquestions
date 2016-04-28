#!/usr/bin/env python3

import csv, sys
file_name = sys.argv[1]

pos = {}
with open(file_name) as f:
    r = csv.reader(f, delimiter=',')
    for s in r:
        if (s[0] == 'qtext'):
            continue
        key = s[0] + ',' + s[2]
        if (s[1] == '1'):
            if (key in pos):
                pos[key] += 1
            else:
                pos[key] = 1
            
outcsv = csv.DictWriter(sys.stdout, fieldnames=['qtext', 'label', 'atext'])
outcsv.writeheader()
with open(file_name) as f:
    r = csv.reader(f, delimiter=',')
    for s in r:
        if (s[0] == 'qtext'):
            continue
        key = s[0] + ',' + s[2] 
        if (key not in pos or s[1] == '1'):
            outcsv.writerow({'qtext':s[0], 'label':s[1], 'atext':s[2]})