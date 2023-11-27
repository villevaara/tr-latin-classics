import os
from lxml import etree
import json
import gzip


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
allfiles = os.listdir('data/raw/corpus-corporum')
for file in allfiles:
    xmlfile = 'data/raw/corpus-corporum/' + file
    tree = etree.parse(xmlfile)
    root = tree.getroot()
    ns = {'ns':'http://www.tei-c.org/ns/1.0'}
    text = root.find('ns:text', ns)
    fulltxt = ''.join(text.itertext())
    thisdata.append({
        'text': fulltxt,
        'doc_id': file})
    outfile = 'data/work/txt/' + file.split('.')[0] + ".txt"
    with open(outfile, 'w') as txtf:
        txtf.write(fulltxt)

# Save lengths of the texts for determining split size for BLAST.
lengths = [len(t['text']) for t in thisdata]
with open('data/work/lengths.txt', 'w') as f:
    l_str = [str(l) + '\n' for l in lengths]
    f.writelines(l_str)


chunk_size = 1000
chunk_i = 0
while len(thisdata) > 0:
    chunkdata = thisdata[:chunk_size]
    outfile = outpath + 'latin_chunk_' + str(chunk_i) + '.json'
    write_json_results(chunkdata, outfile, compress=True)
    chunk_i += 1
    thisdata = thisdata[chunk_size:]
