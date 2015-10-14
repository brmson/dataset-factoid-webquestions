Freebase MIDs of concepts
=========================

The mids of each concept (from d-dump concepts plus d-freebase freebaseKey
annotations) are generated using ``scripts/freebase_mids.py``:

	for s in devtest test train val; do
		echo $s
		scripts/freebase_mids.py $s
	done

Files contain array of json objects each containing qId and freebaseMids array.
The freebaseMids array contains objects with fields ``concept`` and ``mid``.
