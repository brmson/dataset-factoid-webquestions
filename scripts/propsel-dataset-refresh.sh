#!/bin/sh
#
# propsel-dataset-refresh.sh - Regenerate property selection dataset
#
# Usage: scripts/propsel-dataset-refresh.sh YODAQADIR OUTDIR [RELDUMP]
# Example: scripts/propsel-dataset-refresh.sh ../yodaqa propsel/ reldump=true
#
# Parameter reldump=true generates full relation (property) dump.
# Relation dump contains property path(s) from question entity to answer
# including paths from question entity to witness if it is contained in question.
# Referenced script make-propsel-dataset.py requires additional files
# in d-dump and d-freebase-brp directories generated using dump-refresh.sh script.

set -e

yodaqa=$1
outdir=$2
reldump=$3
basedir=$(pwd)

mkdir -p $basedir/d-relation-dump

if [ "$reldump" = "reldump=true" ]; then
	cd "$yodaqa"
	yodaqa_cid=$(git rev-parse --short HEAD)
	for i in devtest test trainmodel val; do
		./gradlew exploringPathDump -PexecArgs="$basedir/main/${i}.json $basedir/d-relation-dump/_${i}.json"
		python data/ml/repair-json.py "$basedir/d-relation-dump/_${i}.json" > "$basedir/d-relation-dump/${i}.json"
		rm "$basedir/d-relation-dump/_${i}.json"
	done
	cd "$basedir"
fi

for s in devtest test trainmodel val; do
	echo $s
	scripts/make-propsel-dataset.py 0 $s $basedir $outdir/$s.csv
done

