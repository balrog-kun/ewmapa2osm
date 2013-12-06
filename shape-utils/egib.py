#! /usr/bin/python3

import sys
import subprocess
import os
import math
import xml.etree.cElementTree as ElementTree
import codecs

# http://www.geobid.katowice.pl/instrukcje/k1-1/zal3.htm
num2chr = {
	218: "GUZ",
	310: "BUI",
	312: "BYN",
	314: "BUN",
	316: "BZO",
	318: "BUO",
	346: "BUW",
	350: "WJD",
	352: "SCH",
	360: "BUF",
	362: "CIE",
	368: "BUR",
	420: "KOU",
	423: "KOC",
	902: "BGS",
}

types = {
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
        "building:type:pl": "Wiata, taras odkryty na podporach",
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
    "WJD": {
        "description:pl": "Wjazd do podziemia",
        "fixme1": "yes",
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
    "BGS": {
        "description:pl": "Ogrodzenie trwałe",
        "barrier": "fence",
    },
}

root = ElementTree.parse(sys.argv[1]).getroot()

sys.stderr.write("Adapting tags...\n")

for elem in root:
	tgs = { sub.attrib['k']: sub.attrib['v']
			for sub in elem if sub.tag == 'tag' }

	if 'TYPLINII' not in tgs:
		continue

	todel = [ 'TYPLINII', 'OPERAT', 'KOLOR', 'WARSTWA' ]
	deltags = [ sub for sub in elem if sub.tag == 'tag' and
			sub.attrib['k'] in todel ]
	for sub in deltags:
		elem.remove(sub)

	numtype = int(tgs['TYPLINII'])
	if numtype in num2chr:
		addtags = types[num2chr[numtype]]
	else:
		addtags = { 'building': 'fixme' }
	addtags['source'] = "Starostwo Powiatowe Strzelce Krajeńskie"
	if '_R' in tgs['WARSTWA']:
        	addtags['source'] += ', raster'
	else:
        	addtags['source'] += ', survey'

	for k in addtags:
		sub = ElementTree.SubElement(elem, "tag", {
			"k": k, "v": addtags[k] })

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write('tagged.osm', "utf-8")
