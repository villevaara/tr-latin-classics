import os
from lxml import etree
import json
import gzip
from helpers import get_clean_id


def write_json_results(outdata, jsonfile, compress=True):
    jsonstring = ""
    for entry in outdata:
        entry_json = json.dumps(entry) + "\n"
        jsonstring += entry_json
    if compress:
        with gzip.open(jsonfile + ".gz", 'wb') as jsonfilegzip:
            json_bytes = jsonstring.encode('utf-8')
            jsonfilegzip.write(json_bytes)
    else:
        with open(jsonfile, 'w') as jsonfile:
            jsonfile.write(jsonstring)


outpath = 'data/final/'

thisdata = []
xmlfile = 'data/raw/biblia/Vulgata_Clementina.xml'
tree = etree.parse(xmlfile)
root = tree.getroot()
ns = {'ns':'http://www.tei-c.org/ns/1.0'}
text = root.find('ns:text', ns).find('ns:body', ns)

testaments = text.findall('ns:div1', ns)

for testament in testaments:
    testament_title = testament.find('ns:head', ns).text
    books = testament.findall('ns:div2', ns)
    for book in books:
        book_title = book.find('ns:head', ns).text
        book_text = ''.join(book.itertext())
        text_id = get_clean_id('Vulgata_Clementina-' + testament_title + "-" + book_title)
        thisdata.append({
            'text': book_text,
            'doc_id': text_id})
        outfile = 'data/work/txt/' + text_id + ".txt"
        with open(outfile, 'w') as txtf:
            txtf.write(book_text)

chunk_size = 1000
chunk_i = 0
while len(thisdata) > 0:
    chunkdata = thisdata[:chunk_size]
    outfile = outpath + 'vulgata_chunk_' + str(chunk_i) + '.json'
    write_json_results(chunkdata, outfile, compress=True)
    chunk_i += 1
    thisdata = thisdata[chunk_size:]
