Freebase MIDs of concepts
=========================

The mids of each concept are generated using ``scripts/mids-from-concepts.py`` from question dump files located in ``d-dump``:

	for s in devtest test train val; do
		python scripts/mids-from-concepts.py d-dump/$s.json > d-freebase-mids/$s.json
	done

Files contain array of json objects each containing qId and freebaseMids array. The freebaseMids array contains objects with fields
concept and mid.

