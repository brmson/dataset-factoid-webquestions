Question dump
=============

This dataset contains dump of LATs, SV and Concepts for each question. It can be generated using YodaQA:

	./gradlew questionDump -PexecArgs="questions.tsv question-dump.json"

The provided tsv file needs to have columns four columns: questionID questionType questionText questionAnswer.

The question-dump.json need to be repaired in order to be proper json format (add '[" to the beggining
of the file and "]" to the end and add "," to the end of every line).
