#!/usr/bin/python
#
# fulldata.py: Create JSON files containing full data available for each question
#
# This merges JSON files from main/ and all the d-*/ directories.
#
# Example: mkdir full; ./fulldata.py full/

import glob
import json
import sys
import datalib


def full_split_data(split):
    data = datalib.QuestionSet()
    for dirname in ['main'] + glob.glob('d-*/'):
        with open('%s/%s.json' % (dirname, split), 'r') as f:
            data.add(json.load(f))
    return data


if __name__ == "__main__":
    outdirname = sys.argv[1]

    for split in ['devtest', 'val', 'trainmodel', 'test']:
        data = full_split_data(split)
        with open('%s/%s.json' % (outdirname, split), 'w') as f:
            datalib.save_json(data.to_list(), f)
