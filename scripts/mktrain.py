#!/usr/bin/python
#
# mktrain.py: Make a train split from devtest+val+trainmodel splits
#
# This recovers the original Berant's train split which you may want
# to use instead of the more fine-grained standard splits.
#
# Example: ./mktrain.py main; ./mktrain.py d-freebase

import json
import sys
import datalib


if __name__ == "__main__":
    dirname = sys.argv[1]

    data = datalib.QuestionSet()
    for split in ['devtest', 'val', 'trainmodel']:
        with open('%s/%s.json' % (dirname, split), 'r') as f:
            data.add(json.load(f))

    with open('%s/train.json' % (dirname,), 'w') as f:
        datalib.save_json(data.to_list(), f)
