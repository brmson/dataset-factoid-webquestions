Movie QA Benchmarking Dataset
=============================

One particular application we consider here is enhancing and speeding up
capability of QA systems to answer "noisy" questions on a structured
knowledge base in a narrow domain.  Here, we choose the "movies" domain,
meant to be answerable using IMDB based data.

	for s in devtest val trainmodel test; do
		cat main/$s.json |
			egrep 'qText.*(play|star[^t]|voice|movie|\bact)' |
			egrep -v 'play[^ ]* (for|4)\b|position|playoff|soccer|music|sport|ball|guitar|tennis' >\
			t-movies/$s.json
	done

The dataset is currently rather noisy and mixed with sports questions.
It will probably get revised before the "v1.0" version.
