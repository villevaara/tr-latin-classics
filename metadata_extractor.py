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
        finalmeta[k] = v
    df = pd.json_normalize(finalmeta, sep='_')
    normalized_d = df.to_dict(orient='records')[0]
    return normalized_d


metadata = []
metakeys = set()
allfiles = os.listdir('data/raw')
for file in allfiles:
    xmlfile = 'data/raw/' + file
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
