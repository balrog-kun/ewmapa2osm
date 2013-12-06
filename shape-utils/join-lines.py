#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# BSD license, 2011 Andrzej Zaborowski

import sys
import math
import xml.etree.cElementTree as ElementTree

long_ways = 0 # Whether to add new nodes without splitting the way
root = ElementTree.parse(sys.argv[1]).getroot()

nodes = {}
ways = {}
minid = 0
for elem in root:
	if 'id' in elem.attrib:
		id = int(elem.attrib['id'])
		if id < minid:
			minid = id
	else:
		continue

	if elem.tag != 'node':
		continue
	nodes[id] = (
			float(elem.attrib['lat']),
			float(elem.attrib['lon']),
			[],
			[],
			elem
		)

for elem in root:
	if elem.tag != 'way':
		continue

	id = int(elem.attrib['id'])

	nds = [ int(sub.attrib['ref']) for sub in elem if sub.tag == 'nd' ]
	ways[id] = ( nds, elem )

	nodes[nds[0]][2].append(id)
	nodes[nds[-1]][2].append(id)
	for nd in nds[1:-1]:
		nodes[nd][3].append(id)

sys.stderr.write("Merging close nodes...\n")

bbox = [ 100000000, 100000000, 0, 0 ]
for id in nodes:
	p = nodes[id]
	if p[0] < bbox[0]:
		bbox[0] = p[0]
	if p[1] < bbox[1]:
		bbox[1] = p[1]
	if p[0] > bbox[2]:
		bbox[2] = p[0]
	if p[1] > bbox[3]:
		bbox[3] = p[1]
y1m = 360.0 / 40000000
x1m = 360.0 / (40000000 * math.cos(p[0] / 180.0 * math.pi))
bbox = [ bbox[0] - 10 * x1m, bbox[1] - 10 * y1m,
		bbox[2] + 10 * x1m, bbox[3] + 10 * y1m ]

idx = {}

def replace(lst, old, new):
	# TODO
	for i in range(0, lst.count(old)):
		lst[lst.index(old)] = new

xsize, ysize = 30 * x1m, 30 * y1m # 30m x 30m
yres = int((bbox[2] - bbox[0]) / xsize) + 1
epsilon = 0.02 # 2cm
todel_nd = {}
for id in nodes:
	p = nodes[id]

	x = int((p[0] - bbox[0]) / xsize)
	y = int((p[1] - bbox[1]) / ysize)
	j = x + y * yres

	pts = []
	if j in idx:
		pts = idx[j]

	merged = 0
	for id2 in pts:
		p2 = nodes[id2]
		if math.hypot((p2[0] - p[0]) / x1m, (p2[1] - p[1]) / y1m) < epsilon:
			merged = 1
			todel_nd[id] = p
			for i in p[2] + p[3]:
				replace(ways[i][0], id, id2)
			p2[2].extend(p[2])
			p2[3].extend(p[3])
			break
	if merged:
		continue

	x0 = int((p[0] - xsize * 0.5 - bbox[0]) / xsize)
	x1 = int((p[0] + xsize * 0.5 - bbox[0]) / xsize)
	y0 = int((p[1] - ysize * 0.5 - bbox[1]) / ysize)
	y1 = int((p[1] + ysize * 0.5 - bbox[1]) / ysize)
	if x0 + y0 * yres not in idx:
		idx[x0 + y0 * yres] = []
	idx[x0 + y0 * yres].append(id)
	if x0 + y1 * yres not in idx:
		idx[x0 + y1 * yres] = []
	idx[x0 + y1 * yres].append(id)
	if x1 + y0 * yres not in idx:
		idx[x1 + y0 * yres] = []
	idx[x1 + y0 * yres].append(id)
	if x1 + y1 * yres not in idx:
		idx[x1 + y1 * yres] = []
	idx[x1 + y1 * yres].append(id)
for id in todel_nd:
	del nodes[id]

sys.stderr.write("Merging close nodes and segments...\n")
# For now without checking the angles

epsilon = 0.02 # 2cm
noconn_epsilon = 0.2 # 20cm
for id in nodes:
	p = nodes[id]
	x = int((p[0] - bbox[0]) / xsize)
	y = int((p[1] - bbox[1]) / ysize)
	j = x + y * yres
	if j not in idx:
		continue
	mindist = noconn_epsilon
	if p[3] or len(p[2]) > 1: ####
		mindist = epsilon
	minseg = []
	for id2 in idx[j]:
		if id2 == id:
			continue
		p2 = nodes[id2]
		for wid in p2[2] + p2[3]:
			way = ways[wid]
			if id in way[0]:
				continue
			if way[0][-1] == id2:
				continue # TODO
			pos = way[0].index(id2)
			a = p2
			b = nodes[way[0][pos + 1]]
			#ab_dist = math.hypot(a[0] - b[0], a[1] - b[1])
			#ap_dist = math.hypot(a[0] - p[0], a[1] - p[1])
			#bp_dist = math.hypot(b[0] - p[0], b[1] - p[1])
			ab_dist_sq = (a[0] - b[0]) / x1m * (a[0] - b[0]) / x1m + \
				(a[1] - b[1]) / y1m * (a[1] - b[1]) / y1m
			ap_dist_sq = (a[0] - p[0]) / x1m * (a[0] - p[0]) / x1m + \
				(a[1] - p[1]) / y1m * (a[1] - p[1]) / y1m
			bp_dist_sq = (b[0] - p[0]) / x1m * (b[0] - p[0]) / x1m + \
				(b[1] - p[1]) / y1m * (b[1] - p[1]) / y1m
			#if ab_dist_sq < 0.003:
			#	continue
			#if cnt == 1:
			#	if ap_dist > ab_dist + epsilon / 2:
			#		continue
			#	if bp_dist > ab_dist + epsilon / 2:
			#		continue
			#else:
			#	if ap_dist > ab_dist - epsilon / 2:
			#		continue
			#	if bp_dist > ab_dist - epsilon / 2:
			#		continue
			if ap_dist_sq > ab_dist_sq:
				continue
			if bp_dist_sq > ab_dist_sq:
				continue
			ab_dist = math.sqrt(ab_dist_sq)
			line_dist = abs((p[0] - a[0]) / x1m * (b[1] - a[1]) / y1m -
				(p[1] - a[1]) / y1m * (b[0] - a[0]) / x1m) / ab_dist
			if line_dist > mindist:
				continue
			if long_ways:
				way[0].insert(pos + 1, id)
				p[3].append(wid)
			else:
				minid -= 1

				# Update the adjacency info in the nodes
				p[2].append(wid)
				p[2].append(minid)
				nodes[way[0][-1]][2].remove(wid)
				nodes[way[0][-1]][2].append(minid)
				for id3 in way[0][pos + 1:-1]:
					nodes[id3][3].remove(wid)
					nodes[id3][3].append(minid)

				# Update the way's node list
				newnds = [ id ] + way[0][pos + 1:]
				way[0][pos + 1:] = [ id ]

				newelem = ElementTree.SubElement(root, "way", {
					"version": str(1), "id": str(minid) })
				for sub in way[1]:
					if sub.tag != 'tag':
						continue
					newsub = ElementTree.SubElement(
							newelem, "tag",
							sub.attrib)
				ways[minid] = ( newnds, newelem )

for id in todel_nd:
	# TODO: tag checks and such
	root.remove(todel_nd[id][4])

for id in ways:
	way = ways[id]
	for sub in [ sub for sub in way[1] if sub.tag == 'nd' ]:
		way[1].remove(sub)
	for nd in way[0]:
		sub = ElementTree.SubElement(way[1], "nd", { "ref": str(nd) })

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write('joined.osm', "utf-8")
