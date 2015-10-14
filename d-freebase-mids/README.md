Freebase MIDs of concepts
=========================

The mids of each concept are generated using ``scripts/freebase_mids.py`` from question dump files located in ``d-dump``:

	for s in devtest test train val; do
		echo $s
		scripts/freebase_mids.py $s
	done

Files contain array of json objects each containing qId and freebaseMids array. The freebaseMids array contains objects with fields
concept and mid.

