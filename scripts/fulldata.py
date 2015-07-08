#!/usr/bin/python
#
# fulldata.py: Create JSON files containing full data available for each question
#
# This merges JSON files from main/ and all the d-*/ directories to full/.
#
# Example: mkdir full; for split in devtest val trainmodel test; do ./fulldata.py $split full/ main/ d-*/; done

import sys
import datalib


if __name__ == "__main__":
    split = sys.argv[1]
    outdirname = sys.argv[2]
    indirnames = sys.argv[3:]

    data = datalib.load_multi_data(split, indirnames)
    with open('%s/%s.json' % (outdirname, split), 'w') as f:
        datalib.save_json(data.to_list(), f)
