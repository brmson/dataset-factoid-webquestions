#!/usr/bin/python3

import datalib, sys, json
from SPARQLWrapper import SPARQLWrapper, JSON

if __name__ == "__main__":
    split = sys.argv[1]
   
    with open('d-relation-dump/' + split + '_.json') as f:
        data = json.load(f)
    # data = datalib.load_multi_data(split, ['d-relation-dump2'])
    url = 'http://freebase.ailao.eu:3030/freebase/query'
    sparql = SPARQLWrapper(url)
    sparql.setReturnFormat(JSON)

    label_cache = {}
    out = open('d-relation-dump/%s.json' % (split,), 'w')
    print('[', file=out)
    for i, line in enumerate(data):
        paths = []
        key = line['qId']
        print('>> %s' % (key,))
        for path in line['exploringPaths']:
            newpath = []
            for prop in path['path']:
                prop = prop[1:].replace("/",".")                
                if (prop not in label_cache):
                    sparql_query = '''
                    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                    PREFIX ns: <http://rdf.freebase.com/ns/>
                    SELECT DISTINCT ?proplabel WHERE { 
                       ns:''' + prop + ''' ns:type.object.name ?proplabel .
                       FILTER( LANGMATCHES(LANG(?proplabel), "en") )
                    } ''' 
                    sparql.setQuery(sparql_query)
                    res = sparql.query().convert()
                    try:
                        proplabel = res['results']['bindings'][0]['proplabel']['value']
                    except IndexError:
                        proplabel = prop.split(".")[-1].replace("_", " ")
                    label_cache[prop] = proplabel
                else:
                    proplabel = label_cache[prop]
                print(proplabel)
                newpath.append({'property': prop, 'label': proplabel})
            tmp = dict(path)
            tmp['path'] = newpath
            paths.append(tmp)
        if (i + 1 == len(data)):
            print(json.dumps({'qId': key, 'exploringPaths': paths}), file=out)
        else:
            print(json.dumps({'qId': key, 'exploringPaths': paths}) + ',', file=out)
    print(']', file=out)
    out.close()
