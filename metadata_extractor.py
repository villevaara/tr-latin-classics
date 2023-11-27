import os
from lxml import etree
import json
import gzip
import xmltodict
import pandas as pd
import csv


def get_item_meta(desc):
    descstr = etree.tostring(desc)
    descdict = list(xmltodict.parse(descstr).values())[0]
    finalmeta = dict()
    for k, v in descdict.items():
        if k == '@xmlns':
            continue
        else:
            finalmeta[k] = v
    for k, v in finalmeta.items():
        if k == 'titleStmt':
            final_v = list()
            if type(v['title']) == list:
                for i in v['title']:
                    if type(i) == str:
                        final_v.append(i)
                    elif type(i) == dict:
                        for key in i.keys():
                            if key == '#text':
                                final_v.append(i[key])
            if len(final_v) > 0:
                v['title'] = '; '.join(final_v)

    df = pd.json_normalize(finalmeta, sep='_')
    normalized_d = df.to_dict(orient='records')[0]
    return normalized_d


metadata = []
metakeys = set()
allfiles = os.listdir('data/raw/corpus-corporum/')
for file in allfiles:
    xmlfile = 'data/raw/corpus-corporum/' + file
    tree = etree.parse(xmlfile)
    root = tree.getroot()
    ns = {'ns':'http://www.tei-c.org/ns/1.0'}
    filedesc = root.find('.//ns:fileDesc', ns)
    item_meta = get_item_meta(filedesc)
    item_meta['doc_id'] = file
    metadata.append(item_meta)
    metakeys.update(list(item_meta.keys()))

metakeys = sorted(list(metakeys))

with open('data/final/metadata.csv', 'w') as csvf:
    fieldnames = list(metakeys)
    writer = csv.DictWriter(csvf, fieldnames=fieldnames)
    writer.writeheader()
    for row in metadata:
        writer.writerow(row)
