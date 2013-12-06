#! /usr/bin/python3
import xml.etree.cElementTree as ElementTree
import sys
import math

sys.stderr.write("Parsing .osm...\n")

root = ElementTree.parse(sys.argv[1]).getroot()
segs = {}
pts = {}
coords = {}
minid = 0

sys.stderr.write("Preparing data...\n")

for elem in root:
	if 'id' in elem.attrib:
		id = int(elem.attrib['id'])
		if id < minid:
			minid = id
	if elem.tag != 'way':
		if elem.tag == 'node':
			coords[id] = (
					float(elem.attrib['lat']),
					float(elem.attrib['lon']),
				)
		continue

	nds = [ int(sub.attrib['ref']) for sub in elem if sub.tag == 'nd' ]
	tgs = { sub.attrib['k']: sub.attrib['v']
			for sub in elem if sub.tag == 'tag' }

	if len(nds) != 2 or nds[0] == nds[1]:
		continue

	nds = sorted(nds)
	tgs['_nds'] = ( nds[0], nds[1] )
	tgs['_elem'] = elem

	# Insert the segment into segs checking for duplicates first
	if tgs['_nds'] in segs:
		continue

	segs[tgs['_nds']] = tgs

	# Insert into the pts hash too, producing an adjacency matrix of sorts
	if nds[0] not in pts:
		pts[nds[0]] = []
	pts[nds[0]].append(tgs)

	if nds[1] not in pts:
		pts[nds[1]] = []
	pts[nds[1]].append(tgs)

sys.stderr.write("Joining segments to form polygons...\n")

def signbit(x):
    if x > 0:
        return 1
    if x < 0:
        return -1

def getangle(a, b, c):
    ablen = math.hypot(b[0] - a[0], b[1] - a[1])
    bclen = math.hypot(c[0] - b[0], c[1] - b[1])

    # Vector cross product (?)
    cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
    # Vector dot product (?)
    dot = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])

    try:
        sine = cross / (ablen * bclen)
        cosine = dot / (ablen * bclen)
        return signbit(sine) * math.acos(cosine)
    except:
        return 0.0

def getangleeq(a, b, c):
    bclen = math.hypot(c[0] - b[0], c[1] - b[1])

    # Vector cross product (?)
    cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
    # Vector dot product (?)
    dot = (b[0] - a[0]) * (c[0] - b[0]) + (b[1] - a[1]) * (c[1] - b[1])

    try:
        sine = cross / bclen
        cosine = dot / bclen
        return signbit(sine) * math.acos(cosine)
    except:
        return -math.pi

ways = {}
for nds in segs:
	seg = segs[nds]
	for dir in [ 0, 1 ]:
		if [ "_d0", "_d1" ][dir] in seg:
			continue

		s = seg
		p = nds

		j = p[dir]
		end = p[1 - dir]
		i = end
		poly = [ ( s, [ "_d0", "_d1" ][dir], j ) ]
		sum = 0
		while j != end:
			a, b = coords[i], coords[j]

			maxangle = -math.pi
			maxedge = None
			for next in pts[j]:
				if next is s:
					continue

				k = next["_nds"][1]
				if k == j:
					k = next["_nds"][0]
					if k == j:
						raise 'same?'

				c = coords[k]

				angle = getangle(a, b, c)
				if angle > maxangle:
					maxangle = angle
					maxedge = next

			if not maxedge:
				break

			s = maxedge
			k = s["_nds"][1]
			ndir = "_d0"
			if k == j:
				k = s["_nds"][0]
				ndir = "_d1"

			if ndir in s:
				break
			if k in [ n[2] for n in poly ]:
				break

			i = j
			j = k

			sum += maxangle
			poly.append(( s, ndir, j ))

		if j != end:
			continue

		# Don't really need to calculate this last angle for that
		# check to work..
		sum += getangle(coords[i], coords[j], coords[poly[0][2]])
		if sum < 0:
			continue

		if len(poly) <= 3:
			continue
		for seg2, ndir, node in poly:
			seg2[ndir] = 0

		attrs = {}
		for seg2, ndir, node in poly:
			for attr in seg2:
				if attr[0] == '_':
					continue
				if attr not in attrs:
					attrs[attr] = {}
				if seg2[attr] not in attrs[attr]:
					attrs[attr][seg2[attr]] = 0
				attrs[attr][seg2[attr]] += 1
		for attr in attrs:
			maxscore = 0
			maxval = None
			for val in attrs[attr]:
				if attrs[attr][val] > maxscore:
					maxscore = attrs[attr][val]
					maxval = val
			attrs[attr] = maxval

		angle = sum / math.pi * 180.0
		if abs(angle - 360) > 0.1:
			attrs['fixme'] = 'Weird outline'
		poly.reverse()
		nd = [ node for s, n, node in poly ]
		ways[str(sorted(nd))] = attrs
		attrs['_nds'] = nd + [ nd[0] ]

for nds in segs:
	seg = segs[nds]
	if '_d0' in seg or '_d1' in seg:
		root.remove(seg['_elem'])
	else:
		sub = ElementTree.SubElement(seg['_elem'], "tag", {
			"k": 'fixme', "v": 'merge' })

for nds in ways:
	way = ways[nds]
	minid -= 1
	elem = ElementTree.SubElement(root, "way", {
		"version": str(1), "id": str(minid) })
	for k in way:
		if k[0] == '_':
			continue
		sub = ElementTree.SubElement(elem, "tag", {
			"k": k, "v": way[k] })
	for nd in way['_nds']:
		sub = ElementTree.SubElement(elem, "nd", { "ref": str(nd) })

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write('merged.osm', "utf-8")
