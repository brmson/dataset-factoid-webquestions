Freebase MIDs of concepts
=========================

The mids of each concept are generated using ``scripts/mids-from-concepts.py`` from question dump files located in ``d-dump``:

	python mids-from-concepts.py d-dump/<split>.json > d-freebase-mids/<split>.json

Files contain array of json objects each containing qId and freebaseMids array. The freebaseMids array contains objects with fileds
concept and mid.

