#!/bin/sh
#
# dump-refresh.sh - Regenerate the YodaQA question dump and dependent data
#
# Usage: scripts/dump-refresh.sh YODAQADIR [GOOGLE_API_KEY]
# Example: scripts/dump-refresh.sh ../yodaqa $googleapikey
#
# This script refreshes the d-dump/ data by running YodaQA from the
# given directory (should contain runnable YodaQA checkout) and dependent
# data like the Freebase MIDs and relpaths.

set -e

yodaqa=$1
googleapikey=$2
basedir=$(pwd)


# Question dump

cd "$yodaqa"
yodaqa_cid=$(git rev-parse --short HEAD)
for i in devtest test trainmodel val; do
	./gradlew questionDump -PexecArgs="$basedir/main/${i}.json $basedir/d-dump/_${i}.json"
	python data/ml/repair-json.py "$basedir/d-dump/_${i}.json" >"$basedir/d-dump/${i}.json"
	rm "$basedir/d-dump/_${i}.json"
done
cd "$basedir"


# Freebase MIDs of concepts

for s in devtest test trainmodel val; do
	echo $s
	scripts/freebase_mids.py $s
done

# Freebase Relation Paths

for split in devtest val trainmodel test; do
	echo $split
	scripts/freebase_relpaths_g.py $split rp $googleapikey
done


# Freebase Branched Relation Paths

for split in devtest val trainmodel test; do
	echo $split
	scripts/freebase_relpaths_g.py $split brp $googleapikey
done


echo "git commit -a -m\"Update with YodaQA $yodaqa_cid\" -m\""  # ...
