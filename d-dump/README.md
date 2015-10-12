Question dump
=============

This dataset contains dump of LATs, SV and Concepts for each question. It can be generated using YodaQA:

	for i in devtest test trainmodel val; do
		./gradlew questionDump -PexecArgs="../dataset-factoid-webquestions/main/${i}.json ../dataset-factoid-webquestions/d-dump/_${i}.json"
		python data/ml/repair-json.py ../dataset-factoid-webquestions/d-dump/_${i}.json >../dataset-factoid-webquestions/d-dump/${i}.json
		rm ../dataset-factoid-webquestions/d-dump/_${i}.json
	done
