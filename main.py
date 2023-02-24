# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

import json
import os
import re
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


def collect_references(resource_definition):
    try:
        list_elements = resource_definition['snapshot']['element']
        filtered_list = filter(lambda element: (element.get('type') and element['type'][0]['code'] == 'Reference'),
                               list_elements)
        mapped_list = map(lambda elem: {'field': elem['id'],
                                        'refs': 'self' if 'targetProfile' not in elem['type'][0].keys() else
                                        elem['type'][0]['targetProfile']}, filtered_list)
        return mapped_list
    except KeyError:
        return []


def json_parse():
    path = './package/'
    pattern = '(?<=StructureDefinition-)(.*?)(?=.json)'
    url_pattern = '([^/]+)/?$'
    structure_definitions = filter(lambda file: "StructureDefinition" in file, os.listdir(path))
    reference_per_type = []
    data_for_df = []
    for definition in structure_definitions:
        f = open(path + definition)
        y = json.loads(f.read())
        resource_name = re.search(pattern, f.name)
        if resource_name:
            print('Processing definition: ', resource_name.group())
            type_references = collect_references(y)
            only_refs = map(lambda reference: reference['refs'], list(type_references))
            for ref_array in only_refs:
                for ref in ref_array:
                    arr = [resource_name.group(), re.search(url_pattern, ref).group()]
                    data_for_df.append(arr)
            reference_per_type.append({'resource': resource_name.group(), 'refs': list(type_references)})
    print(list(data_for_df))
    df = pd.DataFrame(data_for_df, columns=['Resource', 'Reference'])
    G = nx.from_pandas_edgelist(df, source='Resource', target='Reference')
    d = dict(G.degree)
    plt.figure(3, figsize=(48, 48))
    nx.draw(G, pos=nx.spring_layout(G, k=2), node_size=[v * 100 for v in d.values()], width=0.3, with_labels=True)
    plt.savefig("resource_graf.png")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    json_parse()
