#!/usr/bin/python3
#
# Find Freebase relation path between concept URL and answer for each question
#
# Walk the RDF graph with Freebase data up to degree N trying to match
# one of the answers, storing all relations that do lead to one.
#
# Example:
#   mkdir d-freebase-rp
#   N=1
#   for split in devtest val trainmodel test; do echo $split; ./freebase_relpaths.py $split http://freebase.ailao.eu:3030/freebase/query $N; done

from __future__ import print_function

from multiprocessing import Pool
from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import datalib


class QuestionRelPathFinder:
    """ a callable that takes care of producing a relpath dataset record
    for a question """
    def __init__(self, sparql, N):
        self.sparql = sparql
        self.N = N

    def get_mid(self, key):
        sparql_mid_query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?concept WHERE {
                    ?concept <http://rdf.freebase.com/key/en> "''' + key + '''" .
                }
            '''
        self.sparql.setQuery(sparql_mid_query)
        results = self.sparql.query().convert()
        return [r['concept']['value'] for r in results['results']['bindings']][0]


    def concept_rels_match(self, mid, labels):
        """ list all relations of a given concept whose label or string value
        is present in the given set of labels """

        value_filter = ['STR(LCASE(?value)) = "' + l.lower() + '"' for l in labels]

        sparql_rel_query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?rel WHERE {
                    <''' + mid + '''> ?rel ?val .

                    OPTIONAL {
                      ?val rdfs:label ?vallabel .
                      FILTER(LANGMATCHES(LANG(?vallabel), \"en\"))
                    }
                    BIND(IF(BOUND(?vallabel), ?vallabel, ?val) AS ?value)

                    FILTER(''' + ' || '.join(value_filter) + ''')
                }
            '''
        # print(sparql_rel_query)
        self.sparql.setQuery(sparql_rel_query)
        results = self.sparql.query().convert()
        return [[r['rel']['value']] for r in results['results']['bindings']]


    def __call__(self, q):
        mid = self.get_mid(q['freebaseKey'])
        print(q['freebaseKey'], mid, file=sys.stderr)
        relpaths = self.concept_rels_match(mid, set(q['answers']))
        print(q['freebaseKey'], '    ', relpaths, file=sys.stderr)

        return {'qId': q['qId'],
                'relPaths': relpaths}


if __name__ == "__main__":
    split, endpoint, N = sys.argv[1:]

    data = datalib.load_multi_data(split, ['main', 'd-freebase'])

    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)

    # XXX: We would like to write the JSON file as we go, but we need
    # to test for last element in save_json() and things would just
    # get too complicated too needlessly.

    qrpf = QuestionRelPathFinder(sparql, N)
    pool = Pool()
    qrp = pool.imap(qrpf, data.to_list())
    pool.close()
    pool.join()

    with open('d-freebase-rp/%s.json' % (split,), 'w') as f:
        datalib.save_json(qrp, f)
