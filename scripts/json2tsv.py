#!/usr/bin/python
#
# json2tsv.py: Create YodaQA-compatible TSV file from the main JSON file
#
# Example (after running mktrain):
#   mkdir tsv; for s in train test; do ./json2tsv.py main $s tsv/; done

from __future__ import print_function

import io
import json
import sys


if __name__ == "__main__":
    indir, split, outdirname = sys.argv[1:]

    with open('%s/%s.json' % (indir, split), 'r') as f:
        data = json.load(f)

    with io.open('%s/%s.tsv' % (outdirname, split), 'w', encoding='utf8') as f:
        for q in data:
            ansregex = '|'.join(q['answers'])
            qcols = [q['qId'], 'factoid', q['qText'], ansregex]
            print('\t'.join(qcols), file=f)
