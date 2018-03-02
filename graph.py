import json
import random
import itertools


with open('root.json', 'r', encoding='utf-8') as f:
    graph=json.load(f)

illness = {}
start_id = 1000
ill_graph = []
for ill_dictionary in graph:
    # get list of unique id illness
    ill_list = ill_dictionary[list(ill_dictionary.keys())[0]]

    for ill in ill_list:
        if ill not in illness.keys():
            illness[ill] = start_id
            start_id+=1
    # get edges with all neighbors
    ill_graph.extend([x for x in itertools.combinations(ill_list, 2)])

with open('translation.json', 'w+', encoding='utf-8') as t:
    json.dump(illness, t, ensure_ascii=False)

with open('ill_graph.txt', 'w+') as g:
    for pair in ill_graph:
        g.write(str(illness[pair[0]]) + '\t'+str(illness[pair[1]]) + '\n')
