#! /usr/bin/python2
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4

import sys
import os
import xml.etree.cElementTree as ElementTree
import string
import math

def contains(poly, pos):
    cont = 0
    prev = poly[0]
    for node in poly[1:]:
        if (node[1] > pos[1]) != (prev[1] > pos[1]) and pos[0] < node[0] + \
                (prev[0] - node[0]) * (pos[1] - node[1]) / (prev[1] - node[1]):
            cont = not cont
        prev = node
    return cont

def expand(poly, dist):
    ratio = math.cos(math.radians(poly[0][0]))
    p = []
    x = poly[-2]
    y = poly[0]
    for z in poly[1:]:
        v0 = ( y[0] - x[0], (y[1] - x[1]) * ratio )
        v1 = ( z[0] - y[0], (z[1] - y[1]) * ratio )
        l0 = math.hypot(v0[0], v0[1])
        l1 = math.hypot(v1[0], v1[1])
        o = ( -v0[1] / l0 - v1[1] / l1, v0[0] / l0 + v1[0] / l1 )
        d = abs(o[0] * v1[1] - o[1] * v1[0]) / l1;
        l = math.hypot(o[0], o[1])
        # Drop it or leave it?  Drop the point
        if l > 0.2:
            p.append(( y[0] + o[0] * dist / d, y[1] + o[1] * dist / d / ratio))

        x, y = ( y, z )
    p.append(p[0])
    return p

root = ElementTree.parse(sys.argv[1]).getroot()

waynodes = {}
bldgs = []
addrs = []

uniqaddr = {}

import rhr

# Read the building outlines
for elem in root:
    if 'id' not in elem.attrib:
        continue
    if 'action' in elem.attrib and elem.attrib['action'] == 'delete':
        continue

    id = int(elem.attrib['id'])
    if elem.tag == 'node':
        lat = float(elem.attrib['lat'])
        lon = float(elem.attrib['lon'])
        waynodes[id] = ( lat, lon )

    tags = {}
    for sub in elem:
        if sub.tag != 'tag':
            continue
        v = sub.attrib['v'].strip()
        if v:
            tags[sub.attrib['k']] = v

    ####
    if elem.tag == 'node':
        if 'addr:housenumber' not in tags:
            continue
        addrs.append(( lat, lon, tags, elem, [] ))
        name = tags['addr:housenumber']
        if 'addr:street' in tags:
            name += ' ' + tags['addr:street']
        elif 'addr:place' in tags:
            name += ' ' + tags['addr:place']
        else:
            continue
        if name in uniqaddr:
            sys.stderr.write(name + ' is a duplicate\n')
            tags['fixme'] = 'Duplicate address'
            uniqaddr[name]['fixme'] = 'Duplicate address'
        uniqaddr[name] = tags
        continue

    if elem.tag != 'way':
        continue
    if 'building' not in tags or tags['building'] == 'no':
        continue
    if 'addr:housenumber' in tags:
        continue

    # Parse the geometry, store in a convenient format,
    # also find some point in the middle of the outline to be used to
    # speed up distance calculation
    way = []
    refs = []
    j = 0
    lat = 0.0
    lon = 0.0
    for sub in elem:
        if sub.tag != 'nd':
            continue
        ref = int(sub.attrib['ref'])
        if ref not in waynodes:
            continue
        way.append(waynodes[ref])
        refs.append(ref)
        if len(refs) == 1:
            continue
        j += 1
        lat += waynodes[ref][0]
        lon += waynodes[ref][1]
    lat /= j
    lon /= j
    if refs[0] != refs[-1]:
        continue
    if rhr.is_rhr(way[1:]):
        nway = way
    else:
        nway = [] + way
        nway.reverse()
        subs = [ sub for sub in elem if sub.tag == 'nd' ]
        for sub in subs:
            elem.remove(sub)
	    elem.insert(0, sub)
    eway = expand(nway, 4.0 * 360 / 40000000)
    eeway = expand(nway, 9.0 * 360 / 40000000)
    bldgs.append(( lat, lon, way, eway, eeway, tags, elem, [] ))

sys.stdout.write("Matching nodes to buildings\n")
for addr in addrs:
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, btags, elem, newaddrs in bldgs:
        if 'addr:housenumber' in btags:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(way, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[4].append(0)
        break
sys.stdout.write("Matching nodes to buffered buildings\n")
for addr in addrs:
    if addr[4]:
        continue
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, btags, elem, newaddrs in bldgs:
        if 'addr:housenumber' in btags:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(eway, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[4].append(0)
        break
sys.stdout.write("Matching nodes to double-buffered buildings\n")
for addr in addrs:
    if addr[4]:
        continue
    lat, lon = addr[:2]
    # Find what if any building shapes contain this lat/lon
    for elat, elon, way, eway, eeway, btags, elem, newaddrs in bldgs:
        if 'addr:housenumber' in btags or newaddrs:
            continue
        if abs(elat - lat) + abs(elon - lon) > 0.005:
            continue
        if not contains(eeway, ( lat, lon )):
            continue
        newaddrs.append(addr)
        addr[4].append(0)
        break

sys.stdout.write("Bulding new xml\n")
for lat, lon, way, eway, eeway, btags, belem, newaddrs in bldgs:
    # If this building contains only a single address node, copy its tags
    # to the building way and mark the node as no longer needed.
    if len(newaddrs) == 1:
        lat, lon, tags, elem, xxx = newaddrs[0]
        if int(elem.attrib['id']) >= 0:
            elem.attrib['action'] = 'delete'
        else:
            root.remove(elem)

        if 'source' in tags and ('source' not in btags or \
                btags['source'] != tags['source']):
            tags['source:addr'] = tags.pop('source')
        btags.update(tags)

        belem.attrib['action'] = 'modify'

        # Rewrite the tags array
        todel = []
        for subelem in belem:
            if subelem.tag == 'tag':
                todel.append(subelem)
        for k in btags:
            ElementTree.SubElement(belem, 'tag', { 'k': k, 'v': btags[k] })
        for subelem in todel:
            belem.remove(subelem)

sys.stdout.write("Writing .osm's\n")
ElementTree.ElementTree(root).write("output.osm", "utf-8")
