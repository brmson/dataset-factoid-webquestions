Freebase Branched Relation Paths
================================

This specific dataset records a set of relation paths that connect
the key Freebase concept with some answer of the respective question.
Additionally, it conects the key Freebase conceot with some concept from
question dump if this path share relation with path from key Freebase concept 
to some answer. The dataset contains an attribute **relPaths**, which is
a list of path objects; each path object is represented by an
array-stored tuple of

	[path, nMatches]

with **path** being a list of strings with relation names and
**nMatches** being number of answer matches within this path.
The first two relation represents path from key concept to answer
and first and third relation represents path from key concept to
some other concept.

This data has been generated from the Freebase Google API using following command:

	for split in devtest test trainmodel val; do
		echo $split
		python scripts/freebase_branched_relpaths_g.py d-freebase-mids/$split.json d-freebase-rp/$split.json [apikey] > d-freebase-brp/$split.json
	done

Apikey is the key for google freebase api and can be obtained here: https://console.developers.google.com/
The freebase response is stored into fbconcepts directory into the file named <mid>.json.
If the apikey is not provided then the script tries to read existing JSON freebase data dumps from the directory fbconcepts/.
