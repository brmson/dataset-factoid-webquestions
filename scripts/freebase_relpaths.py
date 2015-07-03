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

from SPARQLWrapper import SPARQLWrapper, JSON
import sys
import datalib


def get_mid(key, sparql):
    sparql_mid_query = '''
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            SELECT ?concept WHERE {
                ?concept <http://rdf.freebase.com/key/en> "''' + key + '''" .
            }
        '''
    sparql.setQuery(sparql_mid_query)
    results = sparql.query().convert()
    return [r['concept']['value'] for r in results['results']['bindings']][0]


def concept_rels_match(mid, labels, sparql):
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
    sparql.setQuery(sparql_rel_query)
    results = sparql.query().convert()
    return [[r['rel']['value']] for r in results['results']['bindings']]


def question_relpaths(q, sparql, N):
    mid = get_mid(q['freebaseKey'], sparql)
    print(q['freebaseKey'], mid, file=sys.stderr)
    relpaths = concept_rels_match(mid, set(q['answers']), sparql)
    print('\t', relpaths, file=sys.stderr)

    return {'qId': q['qId'],
            'relPaths': relpaths}


if __name__ == "__main__":
    split, endpoint, N = sys.argv[1:]

    data = datalib.load_multi_data(split, ['main', 'd-freebase'])

    sparql = SPARQLWrapper(endpoint)
    sparql.setReturnFormat(JSON)

    with open('d-freebase-rp/%s.json' % (split,), 'w') as f:
        datalib.save_json([question_relpaths(q, sparql, N) for q in data.to_list()], f)
