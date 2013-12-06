#! /usr/bin/python3
import xml.etree.cElementTree as ElementTree
import sys

sys.stderr.write("Parsing .osm...\n")

root = ElementTree.parse(sys.argv[1]).getroot()

sys.stderr.write("Deduplicating segments...\n")

skips = [
		'3#400-139/2011', '3#1424-23-62',
		'3#400-14/2003', '3#1924-1-9',
		'_', '3#400-39/2005',
]
todel = []
segs = {}
for elem in root:
	if elem.tag != 'way':
		continue

	nds = [ int(sub.attrib['ref']) for sub in elem if sub.tag == 'nd' ]
	tgs = { sub.attrib['k']: sub.attrib['v']
			for sub in elem if sub.tag == 'tag' }

	tgs['_nds'] = str(sorted(nds))
	tgs['_elem'] = elem


	# Insert the segment into segs checking for duplicates first
	if tgs['_nds'] in segs:
		if 'OPERAT' in tgs or tgs['OPERAT'] in skips:
			todel.append(elem)
			continue
		if segs[tgs['_nds']]['OPERAT'] not in skips:
			print(segs[tgs['_nds']]['OPERAT'])
			skips.append(segs[tgs['_nds']]['OPERAT'])
		todel.append(segs[tgs['_nds']]['_elem'])
		del segs[tgs['_nds']]

	segs[tgs['_nds']] = tgs
for elem in todel:
	root.remove(elem)

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write('deduped.osm', "utf-8")
