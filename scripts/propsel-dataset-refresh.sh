#!/bin/sh
#
# propsel-dataset-refresh.sh - Regenerate property selection dataset
#
# Usage: scripts/propsel-dataset-refresh.sh YODAQADIR REPLACE OUTDIR [GOOGLE_API_KEY]
# Example: scripts/propsel-dataset-refresh.sh ../yodaqa 0 propsel/ $key
#
# Referenced script make-propsel-dataset.py requires additional files
# in d-dump and d-freebase-brp directories generated using dump-refresh.sh script.
#
# REPLACE parameter specifies whether the entities will be replaced by ENT_TOK token (value 1) or not (value 0).
# GOOGLE_API_KEY is optional key to google freebase API

set -e

replace=$1
outdir=$2
if [ "$#" -eq 3 ]; then
	googleapikey=$3
fi
basedir=$(pwd)

mkdir -p $basedir/d-relation-dump

# if [ "$reldump" = "reldump=true" ]; then
# 	cd "$yodaqa"
# 	yodaqa_cid=$(git rev-parse --short HEAD)
# 	for i in devtest test trainmodel val; do
# 		./gradlew exploringPathDump -PexecArgs="$basedir/main/${i}.json $basedir/d-relation-dump/_${i}.json"
# 		python data/ml/repair-json.py "$basedir/d-relation-dump/_${i}.json" > "$basedir/d-relation-dump/${i}.json"
# 		rm "$basedir/d-relation-dump/_${i}.json"
# 	done
# 	cd "$basedir"
# fi

for s in devtest test trainmodel val; do
	echo $s
	scripts/freebase_relpaths_dump.py $s $googleapikey
done

for s in devtest test trainmodel val; do
	echo $s
	scripts/query_proplabels.py $s
	rm d-relation-dump/${s}_.json
done

for s in devtest test trainmodel val; do
	echo $s
	scripts/make-propsel-dataset.py $replace $s $basedir $outdir/$s.csv
done

