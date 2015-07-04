#!/usr/bin/python3
#
# Find Freebase relation path between concept URL and answer for each question
#
# Walk the RDF graph with Freebase data up to degree N trying to match
# one of the answers, storing all relations that do lead to one.
#
# N.B. to save time, if we find matching relations for N=1, we do not search N=2
# anymore.
#
# Example:
#   mkdir d-freebase-rp
#   N=2
#   for split in devtest val trainmodel test; do echo $split; ./freebase_relpaths.py $split http://freebase.ailao.eu:3030/freebase/query $N; done

from __future__ import print_function

from collections import Counter
from multiprocessing import Pool
from operator import itemgetter
from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import traceback
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

    def count_paths(self, paths):
        """ given a sequence of raw paths, produce a nice counted set """

        # PREFIX : <http://rdf.freebase.com/ns/>
        path_labels = [tuple([rel.replace('http://rdf.freebase.com/ns/', ':') for rel in path]) for path in paths]

        pl_counter = Counter(path_labels)
        pl_set = sorted([(pl, c) for pl, c in pl_counter.items()], key=itemgetter(1), reverse=True)
        return pl_set

    def sparql_filter(self, labels):
        """ generate sparql WHERE{} sub-query that keeps just the values in labels """

        value_filter = ['STRLANG("' + l.lower() + '", "en")' for l in labels]
        sparql_filter = '''
                    OPTIONAL {
                      FILTER(ISURI(?val))
                      ?val rdfs:label ?vallabel .
                      FILTER(LANGMATCHES(LANG(?vallabel), \"en\"))
                    }
                    BIND(IF(BOUND(?vallabel), ?vallabel, ?val) AS ?value)

                    FILTER(ISLITERAL(?value))
                    FILTER(LCASE(?value) IN (''' + ', '.join(value_filter) + '''))
            '''
        return sparql_filter

    def concept_rels_match(self, mid, labels):
        """ list all relations of a given concept whose label or string value
        is present in the given set of labels """
        sparql_rel_query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?rel WHERE {
                    <''' + mid + '''> ?rel ?val .
                    ''' + self.sparql_filter(labels) + '''
                }
            '''
        # print(sparql_rel_query)
        self.sparql.setQuery(sparql_rel_query)
        results = self.sparql.query().convert()
        return self.count_paths([[r['rel']['value']] for r in results['results']['bindings']])

    def concept_rels2_match(self, mid, labels):
        """ list all relations of a given concept whose label or string value
        is present in the given set of labels, while traversing some other
        node """
        sparql_rel_query = '''
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

                SELECT ?rel0 ?rel1 WHERE {
                    <''' + mid + '''> ?rel0 ?t .
                    FILTER(ISURI(?t))
                    ?t ?rel1 ?val .
                    ''' + self.sparql_filter(labels) + '''
                }
            '''
        # print(sparql_rel_query)
        self.sparql.setQuery(sparql_rel_query)
        results = self.sparql.query().convert()
        return self.count_paths([[r['rel0']['value'], r['rel1']['value']] for r in results['results']['bindings']])

    def __call__(self, q):
        try:
            mid = self.get_mid(q['freebaseKey'])
            print(q['freebaseKey'], mid, file=sys.stderr)
            relpaths = self.concept_rels_match(mid, set(q['answers']))
            if self.N >= 2 and not relpaths:
                print(q['freebaseKey'], '    ', 'N=2', file=sys.stderr)
                relpaths = self.concept_rels2_match(mid, set(q['answers']))
            if self.N > 2:
                raise Exception('only N<=2 is supported')
            print(q['freebaseKey'], '    ', relpaths, file=sys.stderr)
        except:
            traceback.print_exc()
            raise

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

    qrpf = QuestionRelPathFinder(sparql, int(N))
    pool = Pool(processes=1)
    qrp = pool.map(qrpf, data.to_list())
    pool.close()
    pool.join()

    with open('d-freebase-rp/%s.json' % (split,), 'w') as f:
        datalib.save_json(qrp, f)
