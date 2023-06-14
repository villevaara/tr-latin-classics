import os
from lxml import etree
import json
import gzip


# WIP. Not needed for now.

def remove_namespaces(xml_root):
    # Iterate through all XML elements
    for elem in xml_root.getiterator():
        # Skip comments and processing instructions,
        # because they do not have names
        if not (
                isinstance(elem, etree._Comment)
                or isinstance(elem, etree._ProcessingInstruction)
        ):
            # Remove a namespace URI in the element's name
            elem.tag = etree.QName(elem).localname
    # Remove unused namespace declarations
    etree.cleanup_namespaces(xml_root)


thisdata = []
allfiles = os.listdir('../data/raw')
for file in allfiles:
    xmlfile = 'data/raw/' + file
    tree = etree.parse(xmlfile)
    root = tree.getroot()
    remove_namespaces(root)
    text = root.find('text')
    fulltxt = ''.join(text.itertext())
    thisdata.append({
        'text': fulltxt,
        'doc_id': file})


# testing
file = allfiles[0]
xmlfile = 'data/raw/' + file
tree = etree.parse(xmlfile)
root = tree.getroot()
remove_namespaces(root)
text = root.find('text')

for item in text.iter():
    print(item)


import xml.etree.cElementTree as etree


for event, elem in etree.iterparse(xmlfile, events=('start', 'end')):
    if event == 'start':
       print(elem.tag) # use only tag name and attributes here
    elif event == 'end':
       # elem children elements, elem.text, elem.tail are available
       if elem.text is not None and elem.tail is not None:
          print(repr(elem.tail))


text = """<xml>
The captial of <place pid="1">South Africa</place> is <place>Pretoria</place>.
</xml>"""

# ElementTree.fromstring()
parser = XMLParser(target=MyTreeBuilder())
parser.feed(text)
root = parser.close() # return an ordinary Element
