#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# BSD license, 2011 Andrzej Zaborowski

import sys
import subprocess
import os
import math
import xml.etree.cElementTree as ElementTree
import codecs

types = {
    "": {}, "1": {}, "2": {}, "10": {},
    "BUI": {
        "building:type:pl": "Podpora (słup nośny) podcienia, wiaty, galerii",
        "building": "support",
    },
    "BYN": {
        "building:type:pl": "Przyziemie budynku nieognioodpornego",
        "building": "yes",
        "building:fireproof": "no",
    },
    "BZO": {
        "building:type:pl": "Przyziemie budynku ognioodpornego",
        "building": "yes",
        "building:fireproof": "yes",
    },
    "BUW": {
        "building:type:pl": "Blok budynku, wiata, przejazd pod budynkiem",
        #"building": "yes",
    },
    "KOS": {
        "building:type:pl": "Ściana oporowa",
        "building": "wall",
    },
    "KOJ": {
        "description:pl": "Krawężnik jezdni",
        "man_made": "curb",
    },
    "KOC": {
        "description:pl": "Krawężnik chodnika (inna niż jezdni), chodnik",
        "man_made": "curb",
    },
    "KOU": {
        "description:pl": "Krawężnik jezdni, linia zmiany nawierzchni, jezdnia",
        "man_made": "curb",
    },
    "KUB": {
        "building:type:pl": "Budowla podziemna, przejscie podziemne, garaż",
        "layer": "-1",
        "building": "underground",
    },
    "SCH": {
        "building:type:pl": "Schody zewnętrzne",
        "building": "stairs",
        "highway": "steps",
        "_area": "yes",
    },
    "GDE": {
        "description:pl": "Część granicy działki ewidencyjnej",
        "boundary": "parcel",
    },
    "GAO": {
        "description:pl": "Granica obrębu",
        "boundary": "parcel",
    },
    "GUZ": {
        "description:pl": "Granica użytku",
        "boundary": "parcel",
    },
    "GPU": {
        "description:pl": "Granica użytku",
        "boundary": "parcel",
    },
    "GPE": {
        "description:pl": "Działka ewidencyjna",
        "boundary": "parcel",
    },
    "GAK": {
        "description:pl": "Granica państwa",
        "boundary": "administrative",
        "admin_level": "2",
    },
    "GAW": {
        "description:pl": "Granica województwa",
        "boundary": "administrative",
        "admin_level": "4",
    },
    "GAP": {
        "description:pl": "Granica powiatu",
        "boundary": "administrative",
        "admin_level": "6",
    },
    "GAG": {
        "description:pl": "Granica gminy",
        "boundary": "administrative",
        "admin_level": "8",
    },
    "PRH": {
        "description:pl": "Przehaczenie - symbol przynależności do działki",
        "fixme1": "yes",
    },
    "BPB": {
        "description:pl": "Przejazd pod budynkiem",
        "tunnel": "yes",
    },
    "BUF": {
        "description:pl": "Fundament budynku budowli",
        "building": "foundation",
        "building:levels": "0",
    },
    "BUG": {
        "description:pl": "Łącznik napowietrzny budynków ognioodpornych",
        "building": "skyway",
        "building:fireproof": "yes",
    },
    "BUN": {
        "building:type:pl": "Obrys budynku nieognioodpornego",
        "building": "yes",
        "building:fireproof": "no",
    },
    "BUO": {
        "building:type:pl": "Obrys budynku ognioodpornego",
        "building": "yes",
        "building:fireproof": "yes",
    },
    "WCN": {
        "building:type:pl": "Wieża ognioodporna (ciśnień, ppożarowa, widokowa)",
        "building": "yes",
        "building:fireproof": "yes",
    },
    "CIE": {
        "description:pl": "Cieplarnia, szklarnia",
        "building": "greenhouse",
        "building:levels": "1",
    },
    "BUR": {
        "description:pl": "Budynek w ruinie",
        "building": "ruin",
        "historic": "ruins",
    },
    "BZN": {
        "description:pl": "Budynek w ruinie",
        "building": "ruin",
        "historic": "ruins",
    },
    "RMP": {
        "description:pl": "Rampa",
        "building": "ramp",
    },
    "RMP.": {
        "description:pl": "Rampa",
        "building": "ramp",
    },
    "BGT": {
        "description:pl": "Ogrodzenie trwałe, brama w ogrodzeniu",
        "barrier": "fence",
    },
    "BGZ": {
        "description:pl": "Ogrodzenie - żywopłot",
        "barrier": "hedge",
    },
    "SWT": {
        "description:pl": "Świetlik do podziemia",
        "fixme1": "yes",
    },
    "WRU": {
        "description:pl": "Warstwica uzupełniająca",
        "fixme1": "yes",
    },
    "WSQ": {
        "description:pl": "Szczyt skarpy nieumocnionej",
        "fixme1": "yes",
    },
    "SWJ": {
        "description:pl": "Strzałka kierunku wjazdu do podziemia",
        "fixme1": "yes",
        "oneway": "yes",
    },
    "KCI": {
        "description:pl": "Strzałka kierunku cieku",
        "fixme1": "yes",
    },
    "WSP": {
        "description:pl": "Punkt określonej wysokości naturalnej terenu",
        "fixme1": "yes",
    },
    "MSZ": {
        "building:type:pl": "Podpora wielosłupowa przewodu napowietrznego",
        "power": "pole",
        "fixme1": "yes",
    },
}

busealias = {
    "": "m", # Według Instrukcji K-1 1995
    "2h": "h2k",
    "2i": "i2k",
    "4kh": "h4k",
    "h3": "h3k",
    "i2": "i2k",
    "i2z": "i2k",
    "i4z": "i4k",
    "p2": "p2k",
}

buse = {
    "p": {
        "building:use:pl": "Przemysłowy",
        "building": "industrial",
        "landuse": "industrial",
        "building:levels": "1",
    },
    "t": {
        "building:use:pl": "Transportu i łączności",
        "building": "garage",
        "building:levels": "1",
    },
    "h": {
        "building:use:pl": "Handlowo-usługowy",
        "building": "retail",
        "landuse": "retail",
        "building:levels": "1",
    },
    "s": {
        "building:use:pl": "Zbiornik, silos lub budynek magazynowy",
        "building": "storage",
        "building:levels": "1",
    },
    "b": {
        "building:use:pl": "Biurowy",
        "building": "office",
        "building:levels": "1",
    },
    "z": {
        "building:use:pl": "Szpital lub zakład opieki medycznej, socjalnej",
        "building": "healthcare",
        "amenity": "hospital",
        "building:levels": "1",
    },
    "m": {
        "building:use:pl": "Mieszkalny",
        "building": "residential",
        "building:levels": "1",
    },
    "k": {
        "building:use:pl": "Oświaty, nauki, sportowy lub kultury, " + \
                "kultu religijnego",
        "building": "education",
        "building:levels": "1",
    },
    "g": {
        "building:use:pl": "Produkcyjny, usługowy lub gospodarczy " + \
                "dla rolnictwa",
        "building": "manufacture",
        "building:levels": "1",
    },
    "i": {
        "building:use:pl": "Inny niemieszkalny",
        "building": "service",
        "building:levels": "1",
    },

    #(sokolowska 47 dh olimp)
    "kn": {
        "building:use:pl": "Świątynia lub kaplica niekatolicka",
        "name": "Kościół Adwentystów Dnia Siódmego",
        "building": "church",
        "religion": "christian",
        "denomination": "adventist",
    },
    "kc": {
        "building:use:pl": "Świątynia lub kaplica katolicka",
        "building": "church",
        "religion": "christian",
        "denomination": "catholic",
    },
    "hh": {
        "building:use:pl": "Hotel, hostel lub dom studencki",
        "building": "hotel",
        "tourism": "hotel",
        "building:levels": "1",
    },
    "it": {
        "building:use:pl": "Budynek transformatora",
        "building": "electricity",
        "power": "sub_station",
        "building:levels": "1",
    },
    "ip": {
        "building:use:pl": "Inny przemysłowy",
        "building": "industrial",
        "building:levels": "1",
    },
    "r": {
        "building:use:pl": "Ruina",
        "building": "ruin",
        "historic": "ruins",
    },
    "r.": {
        "building:use:pl": "Ruina",
        "building": "ruin",
        "historic": "ruins",
    },
    "waga": {
        "building:use:pl": "Waga",
        "building": "scales",
        "landuse": "industrial",
        "building:levels": '1',
    },
    "ciepl": {
        "building:use:pl": "Szklarnia, cieplarnia",
        "building": "greenhouse",
        "building:levels": '1',
    },
    "ciepl.": {
        "building:use:pl": "Szklarnia, cieplarnia",
        "building": "greenhouse",
        "building:levels": '1',
    },
    "rmp": {
        "building:use:pl": "Rampa",
        "building": "ramp",
        "building:levels": '0',
    },
    "rmp.": {
        "building:use:pl": "Rampa",
        "building": "ramp",
        "building:levels": '0',
    },
    "w bud.": {
        "building": "construction",
        "landuse": "construction",
    },
    "w bud": {
        "building": "construction",
        "landuse": "construction",
    },
    "is": {
        "building:use:pl": "Komenda Miejska Państwowej Straży Pożarnej",
        "building": "fire_station",
        "amenity": "fire_station",
    },
    "f": {
        "building:use:pl": "Fundament",
        "building": "foundation",
        "building:levels": '0',
    },
    "f.": {
        "building:use:pl": "Fundament",
        "building": "foundation",
        "building:levels": '0',
    },
}

from format_ewmapa_egib import *
#from format_powiat_gorzow import *

input = codecs.open(filename, 'r', encoding)

section = None
lnum = -1
sec_lnum = None
attrs = {}

segments = {}
points = {}

def rnd(numstr):
    pos = numstr.find('.')
    if pos >= 0:
        return numstr[:pos + 4] # mm max precision
    return numstr
def add_entity(attrs):
    etype = attrs.pop("type")
    layer = attrs.pop(8)

    if layer not in layers or not layers[layer]["use"]:
        return

    obj = None

    if 30 in attrs:
        p0 = ( rnd(attrs.pop(10)), rnd(attrs.pop(20)), rnd(attrs.pop(30)) )
    else:
        p0 = ( rnd(attrs.pop(10)), rnd(attrs.pop(20)) )
    p1 = None
    if 11 in attrs:
        if 31 in attrs:
            p1 = ( rnd(attrs.pop(11)), rnd(attrs.pop(21)), rnd(attrs.pop(31)) )
        else:
            p1 = ( rnd(attrs.pop(11)), rnd(attrs.pop(21)) )
    if 39 in attrs:
        thickness = attrs.pop(39)

    if etype == "LINE" or etype == "CIRCLE" or \
            etype == "ARC" or etype == "POINT":
        attrs["ewmapa:warstwa"] = layers[layer]["name"]
        attrs["source"] = sourcestr
        if "source" in layers[layer]:
            attrs["source"] += ", " + layers[layer]["source"]
        style = {}
        if "default" in layers[layer]:
            style.update(layers[layer]["default"])
        if 6 in attrs and attrs[6] != 'BYLAYER':
            stylestr = attrs.pop(6).upper()
            if len(stylestr) == 5 and stylestr[1] == '_':
               stylestr = stylestr[2:]
            elif stylestr.startswith('1'):
               stylestr = stylestr[1:]
            if stylestr in types:
                style.update(types[stylestr])
                #style["ewmapa:kod_znakowy"] = stylestr
            else:
                sys.stderr.write("Unknown style " + str(stylestr) +
                        " for line " + repr(attrs) +
                        " at line " + str(lnum) + "\n")
                attrs["fixme2"] = "unknown style " + str(stylestr)
        elif 2 in attrs:
            stylestr = attrs.pop(2).upper()
            if len(stylestr) == 5 and stylestr[1] == '_':
               stylestr = stylestr[2:]
            elif stylestr.startswith('1'):
               stylestr = stylestr[1:]
            if stylestr in types:
                style.update(types[stylestr])
                #style["ewmapa:kod_znakowy"] = stylestr
            else:
                sys.stderr.write("Unknown style " + str(stylestr) +
                        " for line " + repr(attrs) +
                        " at line " + str(lnum) + "\n")
                attrs["fixme2"] = "unknown style " + str(stylestr)
        else:
            #sys.stderr.write("No style information for line " + repr(attrs) +
            #        " at line " + str(lnum) + "\n")
            #attrs["note"] = "no style information"
            pass
        attrs.update(style)
        if 40 in attrs:
            attrs["_radius"] = attrs.pop(40)
        if 50 in attrs:
            attrs["_startangle"] = attrs.pop(50)
        if 51 in attrs:
            attrs["_endangle"] = attrs.pop(51)
    elif etype == "TEXT":
        attrs["_layer"] = layers[layer]["name"]
        attrs["_name"] = attrs.pop(1)
        if 71 in attrs:
            attrs["_text_generation"] = [ "normal", "backward",
                "upside_down" ][int(attrs.pop(71))]
        if 72 in attrs:
            attrs["_alignment"] = [ "left", "center", "right",
                "aligned", "middle", "fit" ][int(attrs.pop(72))]
        if 73 in attrs:
            attrs["_vertical_alignment"] = [ "baseline", "bottom", "middle",
                "top" ][int(attrs.pop(73))]
        attrs["_text_height"] = attrs.pop(40)
        attrs["_text_rotation"] = attrs.pop(50)
        attrs["_oblique_angle"] = attrs.pop(51)
    elif etype == "INSERT":
        attrs["_layer"] = layers[layer]["name"]
        if 50 in attrs:
            attrs["_symbol_rotation"] = attrs.pop(50)
        if 41 in attrs:
            attrs["_symbol_scale"] = attrs.pop(41)
        stylestr = attrs.pop(2).upper()
        if len(stylestr) == 5 and stylestr[1] == '_':
           stylestr = stylestr[2:]
        elif stylestr.startswith('1'):
           stylestr = stylestr[1:]
        if stylestr in types:
            attrs.update(types[stylestr])
            #style["ewmapa:kod_znakowy"] = stylestr
        else:
            sys.stderr.write("Unknown style " + str(stylestr) +
                    " for line " + repr(attrs) +
                    " at line " + str(lnum) + "\n")
            attrs["fixme2"] = "unknown style " + str(stylestr)
    else:
        sys.stderr.write("Unknown entity type " + etype +
                " at line " + str(lnum) + "\n")
        return

    if etype == "CIRCLE" or etype == "ARC":
        ctr = ( float(p0[0]), float(p0[1]) )
        radius = float(attrs['_radius'])
        if '_startangle' in attrs and '_endangle' in attrs:
            a0 = float(attrs['_startangle'])
            a1 = float(attrs['_endangle'])
        else:
            a0, a1 = 0.0, 360.0

        a = a1 - a0
        if a < 0.0:
            a += 360.0

        # TODO: we should also take into account other line segments in the
        # file that may start or end at some point on the arc.

        maxdist = 0.3 # 30cm between approximated and real arc

        # maxdist == radius * (1.0 -
        #     math.cos(math.radians(arcangle / segmentcount / 2)))
        if radius < maxdist:
            segcnt = 2
        else:
            segcnt = int(a / 2 / math.degrees(math.acos(1.0 -
                    maxdist / radius)))
        if a < 180.0:
            segcnt = max(segcnt, 3)
        else:
            segcnt = max(segcnt, 5)

        pts = []
        for i in range(0, segcnt + 1):
            angle = math.radians(a0 + a * i / segcnt)
            pts.append(( str(ctr[0] + radius * math.cos(angle)),
                    str(ctr[1] + radius * math.sin(angle)) ))
    else:
        pts = [ p0 ]
        if p1:
            pts.append(p1)

    arr = points
    if len(pts) > 1:
        arr = segments
    if layer not in arr:
        arr[layer] = []

    for i in range(0, max(len(pts) - 1, 1)):
        seg = {}
        seg.update(attrs)

        p0 = pts[i + 0]
        seg["_p0"] = p0[0] + "x" + p0[1]
        if i < len(pts) - 1:
            p1 = pts[i + 1]
            seg["_p1"] = p1[0] + "x" + p1[1]

        seg["_seglyr"] = layer
        arr[layer].append(seg)

sys.stderr.write("Reading in text and segments...\n")

for line in input:
    lnum += 1
    if lnum & 1:
        name = line.strip()
    else:
        etype = int(line)
        continue

    if sec_lnum == None:
        if name == "SECTION":
            sec_lnum = -1
        continue

    sec_lnum += 1

    if sec_lnum == 0:
        section = name
        continue

    if name == "ENDSEC":
        section = None
        sec_lnum = None
        continue

    if section != "ENTITIES":
        continue

    if etype == 0:
        if attrs:
            add_entity(attrs)
        attrs = { "type": name }
    else:
        if etype in attrs and etype != 100:
            sys.stderr.write("Tag " + str(etype) + " duplicate in object " +
                    repr(attrs) + " on line " + str(lnum) + "\n")
        attrs[etype] = name

input.close()

if attrs:
    add_entity(attrs)

sys.stderr.write("Fixing up street addresses...\n")

streets = []
for arr in [ segments, points ]:
    if road_labels not in arr:
        continue
    for attrs in arr.pop(road_labels):
        if "_name" not in attrs:
            continue
        t = attrs.pop("_name")
        a = float(attrs.pop("_text_rotation"))
        p0 = attrs["_p0"].split("x")
        p0 = ( float(p0[0]), float(p0[1]) )
        if "_p1" in attrs:
            p1 = attrs["_p1"].split("x")
            p1 = ( float(p1[0]), float(p1[1]) )
            p0 = ( (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 )
        streets.append(( p0, a, t ))

for arr in [ segments, points ]:
    if housenumber_labels not in arr:
        continue
    for attrs in arr[housenumber_labels]:
        if "_name" not in attrs:
            continue
        a = float(attrs.pop("_text_rotation"))
        p0 = attrs["_p0"].split("x")
        p0 = ( float(p0[0]), float(p0[1]) )
        if "_p1" in attrs:
            p1 = attrs["_p1"].split("x")
            p1 = ( float(p1[0]), float(p1[1]) )
            p0 = ( (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 )
        mindist = 1000
        street = None
        for sp, sa, sname in streets:
            adiff = sa - a
            while adiff > 300.0:
                adiff -= 360.0
            while adiff < -100.0:
                adiff += 360.0
            tol = 40.0 # Angle difference tolerance
            if (adiff > tol or adiff < -tol) and \
                    (adiff < 180 - tol or adiff > 180 + tol):
                continue

            rad = math.radians(sa)
            per_dist = (sp[0] - p0[0]) * math.sin(rad) - \
                    (sp[1] - p0[1]) * math.cos(rad)
            if (adiff - 90.0) * per_dist > 0.0:
                # Wrong side of the street
                continue

            par_dist = (sp[0] - p0[0]) * -math.cos(rad) - \
                    (sp[1] - p0[1]) * math.sin(rad)
            # 120m perpendicular distance,
            # 0.8km parallel distance.
            if abs(per_dist) >= 120 or abs(par_dist) >= 800:
                continue
            dist = abs(per_dist) * 4 + abs(par_dist) + \
                    abs(abs(adiff - 90) - 90) * 4
            if dist < mindist:
                mindist = dist
                street = sname
        if street is not None:
            attrs["addr:street"] = street
        attrs["addr:housenumber"] = attrs.pop("_name").lower()

sys.stderr.write("Fixing up building attributes...\n")

for arr in [ segments, points ]:
    # TODO: powinnismy rozroznic miedzy numerem nawyzszej kondygnacji i
    # liczba kondygnacji
    for layer in arr:
        for attrs in arr[layer]:
            if "_name" not in attrs:
                continue
            t = attrs.pop("_name").lower()
            #attrs["ewmapa:funkcja"] = t #####
            if t in busealias:
                t = busealias[t]
            levels_attrs = {}
            if t[-1] == "k" or t[-1].isdigit():
                end = len(t)
                if t[-1] == "k":
                    end -= 1
                start = end
                while start > 0 and (t[start - 1].isdigit() or
                        t[start - 1] == '.'):
                    start -= 1
                if start < end:
                    levels_attrs["building:levels"] = t[start:end]
                    t = t[:start]
            if t in busealias:
                t = busealias[t]
            if t in buse:
                attrs.update(buse[t])
            elif t:
                attrs['fixme3'] = 'unknown function ' + str(t)
            attrs.update(levels_attrs)

sys.stderr.write("Merging close nodes...\n")

bbox = [ 100000000, 100000000, 0, 0 ]
for layer in segments:
    for seg in segments[layer]:
        p = seg["_p1"].split("x")
        p = ( float(p[0]), float(p[1]) )
        if p[0] < bbox[0]:
            bbox[0] = p[0]
        if p[1] < bbox[1]:
            bbox[1] = p[1]
        if p[0] > bbox[2]:
            bbox[2] = p[0]
        if p[1] > bbox[3]:
            bbox[3] = p[1]
bbox = [ bbox[0] - 10, bbox[1] - 10, bbox[2] + 10, bbox[3] + 10 ]

idx = {}

xsize, ysize = 20, 20 # 30m x 30m
yres = int((bbox[2] - bbox[0] + 200) / xsize)
epsilon = 0.02 # 2cm
for layer in segments:
    for seg in segments[layer]:
        for pn in [ '_p0', '_p1' ]:
            p = seg[pn].split("x")
            p = ( float(p[0]), float(p[1]) )

            x = int((p[0] - bbox[0]) / xsize)
            y = int((p[1] - bbox[1]) / ysize)
            j = x + y * yres

            pts = []
            if j in idx:
                pts = idx[j]

            merged = 0
            for pt in pts:
                if math.hypot(pt[0] - p[0], pt[1] - p[1]) < epsilon:
                    seg[pn] = pt[2]
                    seg[pn + 'f'] = ( pt[0], pt[1] )
                    merged = 1
                    break
            if merged:
                continue
            seg[pn + 'f'] = p

            w = ( p[0], p[1], seg[pn] )
            x0 = int((p[0] - xsize * 0.5 - bbox[0]) / xsize)
            x1 = int((p[0] + xsize * 0.5 - bbox[0]) / xsize)
            y0 = int((p[1] - ysize * 0.5 - bbox[1]) / ysize)
            y1 = int((p[1] + ysize * 0.5 - bbox[1]) / ysize)
            if x0 + y0 * yres not in idx:
                idx[x0 + y0 * yres] = []
            idx[x0 + y0 * yres].append(w)
            if x0 + y1 * yres not in idx:
                idx[x0 + y1 * yres] = []
            idx[x0 + y1 * yres].append(w)
            if x1 + y0 * yres not in idx:
                idx[x1 + y0 * yres] = []
            idx[x1 + y0 * yres].append(w)
            if x1 + y1 * yres not in idx:
                idx[x1 + y1 * yres] = []
            idx[x1 + y1 * yres].append(w)

sys.stderr.write("Removing overlapping segments...\n")

segs = {}
for layer in segments:
    i = 0
    while i < len(segments[layer]):
        s = segments[layer][i]
        if s["_p0"] > s["_p1"]:
            idx = s["_p0"] + 'x' + s["_p1"]
        else:
            idx = s["_p1"] + 'x' + s["_p0"]
        if idx in segs:
            segs[idx].update(s)
            del segments[layer][i]
        else:
            segs[idx] = s
            i += 1
segs = None

sys.stderr.write("Building a segment index...\n")

idx = {}

xsize, ysize = 30, 30 # 30m x 30m
yres = int((bbox[2] - bbox[0] + 200) / xsize)
def add_seg_to_idx(seg):
    if seg["_p0f"][0] < seg["_p1f"][0]:
        x0 = int((seg["_p0f"][0] - xsize * 0.2 - bbox[0]) / xsize)
        x1 = int((seg["_p1f"][0] + xsize * 0.2 - bbox[0]) / xsize)
    else:
        x0 = int((seg["_p1f"][0] - xsize * 0.2 - bbox[0]) / xsize)
        x1 = int((seg["_p0f"][0] + xsize * 0.2 - bbox[0]) / xsize)
    if seg["_p0f"][1] < seg["_p1f"][1]:
        y0 = int((seg["_p0f"][1] - ysize * 0.2 - bbox[1]) / ysize)
        y1 = int((seg["_p1f"][1] + ysize * 0.2 - bbox[1]) / ysize)
    else:
        y0 = int((seg["_p1f"][1] - ysize * 0.2 - bbox[1]) / ysize)
        y1 = int((seg["_p0f"][1] + ysize * 0.2 - bbox[1]) / ysize)
    for xx in range(x0, x1 + 1):
        for yy in range(y0, y1 + 1):
            if xx + yy * yres not in idx:
                idx[xx + yy * yres] = []
            idx[xx + yy * yres].append(seg)
for layer in segments:
    for seg in segments[layer]:
        add_seg_to_idx(seg)

sys.stderr.write("Merging close nodes and segments...\n")

adjacency_cnt = {}
for layer in segments:
    for seg in segments[layer]:
        for pn in [ '_p0', '_p1' ]:
            p = seg[pn]
            if p not in adjacency_cnt:
                adjacency_cnt[p] = 0
            adjacency_cnt[p] += 1

epsilon = 0.06 # 6cm
noconn_epsilon = 0.5 # 50cm
for layer in segments:
    if layers[layer]['type'] != 'spatial':
        continue
    toappend = []
    for seg in segments[layer]:
        for pn in [ ( '_p0f', '_p1f' ), ( '_p1f', '_p0f' ) ]:
            p = seg[pn[0]]
            cnt = adjacency_cnt[seg[pn[0][:3]]]
            p2 = seg[pn[1]]
            x = int((p[0] - bbox[0]) / xsize)
            y = int((p[1] - bbox[1]) / ysize)
            j = x + y * yres
            if j not in idx:
                continue
            mindist = noconn_epsilon
            if cnt > 1:
                mindist = epsilon
            minseg = []
            for seg2 in idx[j]:
                if seg is seg2:
                    continue
                a, b = seg2['_p0f'], seg2['_p1f']
                #ab_dist = math.hypot(a[0] - b[0], a[1] - b[1])
                #ap_dist = math.hypot(a[0] - p[0], a[1] - p[1])
                #bp_dist = math.hypot(b[0] - p[0], b[1] - p[1])
                ab_dist_sq = (a[0] - b[0]) * (a[0] - b[0]) + \
                        (a[1] - b[1]) * (a[1] - b[1])
                ap_dist_sq = (a[0] - p[0]) * (a[0] - p[0]) + \
                        (a[1] - p[1]) * (a[1] - p[1])
                bp_dist_sq = (b[0] - p[0]) * (b[0] - p[0]) + \
                        (b[1] - p[1]) * (b[1] - p[1])
                if ab_dist_sq < 0.003:
                    continue
                #if cnt == 1:
                #    if ap_dist > ab_dist + epsilon / 2:
                #        continue
                #    if bp_dist > ab_dist + epsilon / 2:
                #        continue
                #else:
                #    if ap_dist > ab_dist - epsilon / 2:
                #        continue
                #    if bp_dist > ab_dist - epsilon / 2:
                #        continue
                if ap_dist_sq > ab_dist_sq or ap_dist_sq < 0.000001:
                    continue
                if bp_dist_sq > ab_dist_sq or bp_dist_sq < 0.000001:
                    continue
                ab_dist = math.sqrt(ab_dist_sq)
                line_dist = abs((p[0] - a[0]) * (b[1] - a[1]) -
                        (p[1] - a[1]) * (b[0] - a[0])) / ab_dist
                if line_dist > mindist + 0.01:
                    continue
                if line_dist > epsilon:
                    seg_len = math.hypot(p2[0] - p[0], p2[1] - p[1])
                    p2_dist = abs((p2[0] - a[0]) * (b[1] - a[1]) -
                            (p2[1] - a[1]) * (b[0] - a[0])) / ab_dist
                    if p2_dist < line_dist + seg_len * 0.9 and \
                            (cnt > 1 or p2_dist < noconn_epsilon):
                        continue
                if line_dist > mindist - 0.01 or line_dist < epsilon:
                    minseg.append(seg2)
                    continue
                mindist = line_dist
                minseg = [ seg2 ]
            for seg2 in minseg:
                newseg = {}
                newseg.update(seg2)
                seg2['_p1'] = seg[pn[0][:3]]
                newseg['_p0'] = seg[pn[0][:3]]
                seg2['_p1f'] = p
                newseg['_p0f'] = p

                toappend.append(newseg)
                add_seg_to_idx(newseg)
                adjacency_cnt[seg[pn[0][:3]]] += 2
    #segments[layer] += toappend
    for seg in toappend:
        segments[seg['_seglyr']].append(seg)

idx = None

sys.stderr.write("Removing overlapping segments again...\n")

segs = {}
for layer in segments:
    i = 0
    while i < len(segments[layer]):
        s = segments[layer][i]
        if s["_p0"] > s["_p1"]:
            idx = s["_p0"] + 'x' + s["_p1"]
        else:
            idx = s["_p1"] + 'x' + s["_p0"]
        if idx in segs:
            segs[idx].update(s)
            del segments[layer][i]
        else:
            segs[idx] = s
            i += 1
segs = None

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

nodes = {}
for layer in segments:
    for attrs in segments[layer]:
        if attrs["_p0"] not in nodes:
            nodes[attrs["_p0"]] = []
        nodes[attrs["_p0"]].append(attrs)
        if attrs["_p1"] not in nodes:
            nodes[attrs["_p1"]] = []
        nodes[attrs["_p1"]].append(attrs)

finalnodes = {}
finalways = {}
for layer in segments:
    for seg in segments[layer]:
        for dir in [ 0, 1 ]:
            if [ "_d0", "_d1" ][dir] in seg:
                continue

            s = seg
            p = ( s["_p0"], s["_p1"] )
            if p[0] == p[1]:
                #sys.stderr.write("Segment " + repr(s) + " has only one end?\n")
                continue

            j = p[dir]
            end = p[1 - dir]
            i = end
            #poly = [ ( s["_id"], [ "_d0", "_d1" ][dir], j ),
            #        ( s["_id"], [ "_d0", "_d1" ][dir], end ) ]
            poly = [ ( s, [ "_d0", "_d1" ][dir], j ) ]
            sum = 0
            while j != end:
                a, b = i.split("x"), j.split("x")
                a, b = ( float(a[0]), float(a[1]) ), \
                    ( float(b[0]), float(b[1]) )

                maxangle = -math.pi
                maxedge = None
                for next in nodes[j]:
                    if next is s:
                        continue

                    k = next["_p1"]
                    ndir = "_d0"
                    if k == j:
                        k = next["_p0"]
                        ndir = "_d1"
                        if k == j:
                            #sys.stderr.write("Segment " + repr(s) +
                            #        " has only one end?\n")
                            continue

                    # Zero tolerance: we do these checks only for the
                    # winning edge and discard the entire path, not just
                    # that candidate
                    #if ndir in next:
                    #    continue
                    #if k in [ n[2] for n in poly ]:
                    #    continue

                    # Should we check that next["style"] == s["style"]??

                    c = k.split("x")
                    c = ( float(c[0]), float(c[1]) )

                    angle = getangle(a, b, c)
                    if angle > maxangle:
                        maxangle = angle
                        maxedge = next

                if not maxedge:
                    break

                s = maxedge
                k = s["_p1"]
                ndir = "_d0"
                if k == j:
                    k = s["_p0"]
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

            # Note: no need to add the angle at the last vertex, that is
            # between the current (k, j, p[dir])
            if sum < 0:
                continue

            for seg2, ndir, node in poly:
                seg2[ndir] = 0
            if len(poly) <= 3:
                continue

            for seg2, ndir, node in poly:
                finalnodes[node] = {}
            nd = [ node for s, n, node in poly ]

            attrs = {}
            for seg2, ndir, node in poly:
                for attr in seg2:
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
                if maxscore > 1:
                    attrs[attr] = maxval

            finalways[",".join(sorted(nd))] = {
                "nd": nd + [ nd[0] ],
                "attrs": attrs,
            }
if 0:
    #finalnodes = {}
    #finalways = {}
    for layer in segments:
        for seg in segments[layer]:
            if "_d0" in seg or "_d0" in seg:
                continue

            finalnodes[seg["_p0"]] = {}
            finalnodes[seg["_p1"]] = {}
            nd = [ seg["_p0"], seg["_p1"] ]
            finalways[",".join(nd)] = {
                "nd": nd,
                "attrs": seg,
            }
nodes = None

sys.stderr.write("Building shape index...\n")

def area(poly):
    a = 0
    j = poly[-1]
    for i in poly:
        a += j[0] * i[1] - i[0] * j[1]
        j = i
    return 0.5 * abs(a)

idx = {}

xsize, ysize = 100, 100 # 100m x 100m
yres = int((bbox[2] - bbox[0] + 200) / xsize)
for w in finalways:
    nd = finalways[w]['nd']
    floatnd = [ ( float(p[0]), float(p[1]) ) for p in \
            [ p.split('x') for p in nd ] ]
    p = floatnd[0]
    finalways[w]['floatnd'] = floatnd
    finalways[w]['area'] = area(floatnd)
    x0 = int((p[0] - xsize * 0.5 - bbox[0]) / xsize)
    x1 = int((p[0] + xsize * 0.5 - bbox[0]) / xsize)
    y0 = int((p[1] - ysize * 0.5 - bbox[1]) / ysize)
    y1 = int((p[1] + ysize * 0.5 - bbox[1]) / ysize)
    if x0 + y0 * yres not in idx:
        idx[x0 + y0 * yres] = []
    idx[x0 + y0 * yres].append(w)
    if x0 + y1 * yres not in idx:
        idx[x0 + y1 * yres] = []
    idx[x0 + y1 * yres].append(w)
    if x1 + y0 * yres not in idx:
        idx[x1 + y0 * yres] = []
    idx[x1 + y0 * yres].append(w)
    if x1 + y1 * yres not in idx:
        idx[x1 + y1 * yres] = []
    idx[x1 + y1 * yres].append(w)

sys.stderr.write("Moving tags from text labels to shapes...\n")

# Should we rather check the polygons convex hull instead?
def point_in_poly(pt, poly):
    ret = 0
    p0 = None
    for p1 in poly:
        if p0 is not None and (p1[1] > pt[1]) != (p0[1] > pt[1]) and \
                (pt[0] - p1[0]) < (p0[0] - p1[0]) *\
                (pt[1] - p1[1]) / (p0[1] - p1[1]):
            ret = not ret
        p0 = p1
    return ret

for arr in [ segments, points ]:
    for layer in arr:
        if not layers[layer]['type'].startswith('attrib'):
            continue
        if layers[layer]['type'] == 'attrib-point':
            for attrs in arr[layer]:
                finalnodes[attrs['_p0']] = attrs
            continue
        for attrs in arr[layer]:
            if "_d0" in attrs or "_d1" in attrs:
                continue
            p0 = attrs["_p0"].split("x")
            p0 = ( float(p0[0]), float(p0[1]) )
            p = [ p0 ]
            if "_p1" in attrs:
                p1 = attrs["_p1"].split("x")
                p1 = ( float(p1[0]), float(p1[1]) )
                #p.append(p1)
                p0 = ( (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 )
                #p.append(p0)
                p = [ p0 ]

            poly = None
            x = int((p0[0] - bbox[0]) / xsize)
            y = int((p0[1] - bbox[1]) / ysize)
            j = x + y * yres
            maxarea = 100000000
            for pt in p:
                if j not in idx:
                    continue
                for i in idx[j]:
                    nd = finalways[i]["nd"]
                    floatnd = finalways[i]["floatnd"]
                    if nd[0] == nd[-1] and finalways[i]['area'] < maxarea and \
                            point_in_poly(pt, floatnd):
                        poly = i
                        maxarea = finalways[i]['area']
            if not poly:
                finalnodes[attrs['_p0']] = attrs
                continue

            if "add_tags" not in finalways[poly]:
                finalways[poly]["add_tags"] = []
            finalways[poly]["add_tags"].append(attrs)
segments = None
points = None
idx = None

# TODO: filter by size perhaps
for i in finalways:
    attrs = finalways[i]["attrs"]
    if "_area" in attrs:
        attrs["area"] = "yes"

    if "add_tags" not in finalways[i]:
        continue

    conflicts = {}
    newtags = {}
    addr_cnt = len([ a for a in finalways[i]['add_tags'] \
            if 'addr:housenumber' in a ])
    for a in finalways[i]["add_tags"]:
        if 'addr:housenumber' in a and addr_cnt != 1:
            finalnodes[a['_p0']] = a
            continue
        for prop in a:
            if type(prop) != str or prop[0] == '_':
                continue
            if prop in newtags and newtags[prop] != a[prop]:
                conflicts[prop] = 0
        newtags.update(a)
    attrs.update(newtags)
    if conflicts:
        attrs['fixme4'] = 'Conflicting tags: ' + str(list(conflicts.keys()))

sys.stderr.write("Assigning ids and transforming coordinates to lat/lon...\n")

narr = []
csinput = ""
for i in finalnodes:
    xy = i.split("x")
    narr.append(i)
    csinput += str(xy[0]) + " " + str(xy[1]) + "\n"
cmd = [ #"strace",
        "cs2cs",
        "+proj=tmerc", "+lat_0=0", "+lon_0=18", "+k=0.999923",
        "+x_0=6500000", "+y_0=0", "+ellps=GRS80", "+units=m", "+no_defs",
        "+to",
        "+proj=latlong", "+ellps=WGS84", "+datum=WGS84", "+no_defs",
        "-s",
        "-f", "%.7f" ]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
ret = p.communicate(csinput.encode("utf8"))[0].decode("utf8")
csinput = None

nid = 1
for i, line in enumerate(ret.split("\n")):
    if len(line) < 3:
        if i < len(finalnodes):
            raise Exception("error reprojecting")
        break
    lat, lon, _ = line.split(None, 2)
    finalnodes[narr[i]]["_id"] = str(nid)
    finalnodes[narr[i]]["_lat"] = lat
    finalnodes[narr[i]]["_lon"] = lon
    nid += 1
narr = None
ret = None

wid = 1
for i in finalways:
    finalways[i]["id"] = str(wid)
    wid += 1

sys.stderr.write("Building .osm tree...\n")

root = ElementTree.Element("osm", { "version": "0.6" })
for nodeid in finalnodes:
    node = ElementTree.SubElement(root, "node", {
        "lat": finalnodes[nodeid]["_lat"],
        "lon": finalnodes[nodeid]["_lon"],
        "version": str(1),
        "id": finalnodes[nodeid]["_id"], })

    if 'source' not in finalnodes[nodeid]:
        finalnodes[nodeid]['source'] = sourcestr

    for prop in finalnodes[nodeid]:
        if type(prop) != str or prop[0] == "_":
            continue
        ElementTree.SubElement(node, "tag",
                { "k": prop, "v": str(finalnodes[nodeid][prop]) })

for wayid in finalways:
    way = finalways[wayid]

    if "add_tags" not in way and way['area'] > 200:
        continue

    node = ElementTree.SubElement(root, "way", {
        "version": str(1),
        "id": way["id"] })

    if 'source' not in way["attrs"]:
        way["attrs"]['source'] = sourcestr

    for prop in way["attrs"]:
        if type(prop) != str or prop[0] == "_":
            continue
        ElementTree.SubElement(node, "tag",
                { "k": prop, "v": str(way["attrs"][prop]) })

    for nd in way["nd"]:
        ElementTree.SubElement(node, "nd", { "ref": finalnodes[nd]["_id"] })
finalnodes = None
finalways = None

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write("budynki.osm", "utf-8")
