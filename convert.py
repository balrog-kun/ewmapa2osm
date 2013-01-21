#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# Copyright (c) 2011  Andrzej Zaborowski

import sys
import subprocess
import os
import math
import xml.etree.cElementTree as ElementTree
import codecs

filename = 'rudaslaska.dxf'
sourcestr = 'UM Ruda Śląska'

input = codecs.open(filename, 'r', 'cp1250')

types = {
    "1": {}, "10": {},
    "BUI": {
        "building:type:pl": "Podpora (słup nośny) podcienia, wiaty, galerii",
        "building": "support",
    },
    "BYN": {
        "building:type:pl": "Przyziemie budynku nieognioodpornego",
        #"building": "yes",
        "building:fireproof": "no",
    },
    "BZO": {
        "building:type:pl": "Przyziemie budynku ognioodpornego",
        #"building": "yes",
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
        "fixme": "yes",
    },
    "WRU": {
        "description:pl": "Warstwica usupełniająca",
        "fixme": "yes",
    },
    "WSQ": {
        "description:pl": "Szczyt skarpy nieumocnionej",
        "fixme": "yes",
    },
}

layers = {
    "EADOD_T_0": {
        "type": "attrib",
        "name": "Nazwa ulicy, placu, miejscowości",
        "use": 1,
    },
    "EADTD_T_0": {
        "type": "attrib",
        "name": "Numer adresowy",
        "use": 1,
    },
    "EBUOA_T_0": {
        "type": "attrib",
        "name": "Funkcja, numer najwyzszej kondygnacji, " + \
            "budynku nieognioodpornego",
        "use": 1,
        "default": { "building:fireproof": "no" },
    },
    "EBUOA_T_1": {
        "type": "attrib",
        "name": "Funkcja, numer najwyzszej kondygnacji, budynku ognioodpornego",
        "use": 1,
        "default": { "building:fireproof": "yes" },
    },
    "EBUOA_T_2": {
        "type": "attrib",
        "name": "Opis wieży ognioodpornej będącej budynkiem",
        "use": 1,
        "default": { "building": "tower", "building:fireproof": "yes" },
    },
    "EBUOA_T_3": {
        "type": "attrib",
        "name": "Etykieta 'wtr' wiatraku ognioodpornego będącego budynkiem",
        "use": 1,
        "default": { "building": "windmill", "building:fireproof": "yes" },
    },
    "EBUOA_T_4": {
        "type": "attrib",
        "name": "Etykieta 'wtr' wiatraku nieognioodpornego będącego budynkiem",
        "use": 1,
        "default": { "building": "windmill", "building:fireproof": "no" },
    },
    "EBUOA_T_5": {
        "type": "attrib",
        "name": "Etykieta 'ciepl.' cieplarni, szklarni",
        "use": 1,
        "default": { "building": "greenhouse" },
    },
    "EBUOA_T_6": {
        "type": "attrib",
        "name": "Etykieta 'r.' bydunku w ruinie",
        "use": 1,
        "default": { "building": "ruin", "historic": "ruins" },
    },
    "EBTOO_T_0": {
        "type": "attrib",
        "name": "Liczba kondygnacji budynku ognioodpornego",
        "use": 1,
        "default": { "building:fireproof": "yes" },
    },
    "EBTOO_T_1": {
        "type": "attrib",
        "name": "Liczba kondygnacji budynku nieognioodpornego",
        "use": 1,
        "default": { "building:fireproof": "no" },
    },
    "EBTOO_T_2": {
        "type": "attrib",
        "name": "Opis wieży ognioodpornej, etykieta wiatraku ognioodpornego",
        "use": 1,
        "default": { "building:fireproof": "yes" },
    },
    "EBTOO_T_3": {
        "type": "attrib",
        "name": "Etykieta 'wtr' wiatraku nieognioodpornego " + \
                "nie będącego budynkiem",
        "use": 1,
        "default": { "building": "windmill", "building:fireproof": "no" },
    },
    "EBTOO_T_4": {
        "type": "attrib",
        "name": "Liczba kondygnacji łącznika napowietrznego budynków",
        "use": 1,
        "default": { "building": "skyway" },
    },
    "EBTOO_T_5": {
        "type": "attrib",
        "name": "Etykieta 'rmp.' rampy",
        "use": 1,
        "default": { "building": "ramp" },
    },
    "EBTOO_T_6": {
        "type": "attrib",
        "name": "Etykieta 'f.' fundamentu",
        "use": 1,
        "default": { "building": "foundation", "building:levels": "0" },
    },
    "EBTOO_T_7": {
        "type": "attrib",
        "name": "Strzałka kierunku wjazdu do podziemia",
        "use": 0,
    },
    "EBTOO_T_8": {
        "type": "attrib",
        "name": "Komin - symbol",
        "use": 1,
        "default": { "building": "chimney", "building:use:pl": "Komin" },
    },
    "EBUPP_L_0": {
        "type": "spatial",
        "name": "Przyziemie budynku nieognioodpornego, podpory, podcienia " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPP_L_1": {
        "type": "spatial",
        "name": "Przyziemie budynku ognioodpornego, podpory, podcienia " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "yes" },
    },
    "EBUPP_L_2": {
        "type": "spatial",
        "name": "Przyziemie budynku nieognioodpornego, podpory, podcienia " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPP_L_3": {
        "type": "spatial",
        "name": "Przyziemie budynku ognioodpornego, podpory, podcienia " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "yes" },
    },
    "EBUPO_L_0": {
        "type": "spatial",
        "name": "Obrys budynku nieognioodpornego, podpory, podcienia " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPO_L_1": {
        "type": "spatial",
        "name": "Obrys budynku ognioodpornego, podpory, podcienia " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "yes" },
    },
    "EBUPO_L_2": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny będący budynkiem " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "tower", "building:fireproof": "yes" },
    },
    "EBUPO_L_3": {
        "type": "spatial",
        "name": "Cieplarnia, szklarnia, wiatrak nieognioodporny " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPO_L_4": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny będący budynkiem " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "ruin", "historic": "ruins" },
    },
    "EBUPO_L_5": {
        "type": "spatial",
        "name": "Obrys budynku nieognioodpornego, podpory, podcienia " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPO_L_6": {
        "type": "spatial",
        "name": "Obrys budynku ognioodpornego, podpory, podcienia " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "yes" },
    },
    "EBUPO_L_7": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny będący budynkiem " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "tower", "building:fireproof": "yes" },
    },
    "EBUPO_L_8": {
        "type": "spatial",
        "name": "Cieplarnia, szklarnia, wiatrak nieognioodporny " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes", "building:fireproof": "no" },
    },
    "EBUPO_L_9": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny będący budynkiem " + \
            "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "ruin", "historic": "ruins" },
    },
    "EBTPO_L_0": {
        "type": "spatial",
        "name": "Blok budynku, wiata, przejazd pod budynkiem " + \
            "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "yes" },
    },
    "EBTPO_L_1": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny niebędące " + \
                "budynkiem, komin" + \
                "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "tower", "building:fireproof": "yes" },
    },
    "EBTPO_L_2": {
        "type": "spatial",
        "name": "Inne " + \
                "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
    },
    "EBTPO_L_3": {
        "type": "spatial",
        "name": "Łącznik napowietrzny budynków nieognioodpornych " + \
                "z pomiaru w terenie",
        "source": "survey",
        "use": 1,
        "default": { "building": "skyway", "building:fireproof": "yes" },
    },
    "EBTPO_L_4": {
        "type": "spatial",
        "name": "Blok budynku, wiata, przejazd pod budynkiem " + \
                "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "yes" },
    },
    "EBTPO_L_5": {
        "type": "spatial",
        "name": "Wieża ognioodporna, wiatrak ognioodporny niebędące " + \
                "budynkiem, komin" + \
                "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "tower", "building:fireproof": "yes" },
    },
    "EBTPO_L_6": {
        "type": "spatial",
        "name": "Inne " + \
                "z rastra",
        "source": "raster",
        "use": 1,
    },
    "EBTPO_L_7": {
        "type": "spatial",
        "name": "Łącznik napowietrzny budynków nieognioodpornych " + \
                "z rastra",
        "source": "raster",
        "use": 1,
        "default": { "building": "skyway", "building:fireproof": "yes" },
    },
    "EDZPD_L_0": {
        "type": "spatial",
        "name": "Granica działki ewidencyjnej",
        "use": 0,
    },
    "EDZTD_T_0": {
        "type": "text",
        "name": "Numer ewidencyjny działki",
        "use": 0,
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

section = None
lnum = -1
sec_lnum = None
attrs = {}

segments = {}
points = {}

def add_entity(attrs):
    etype = attrs.pop("type")
    layer = attrs.pop(8)

    if layer not in layers or not layers[layer]["use"]:
        return

    obj = None

    if 30 in attrs:
        p0 = ( attrs.pop(10), attrs.pop(20), attrs.pop(30) )
    else:
        p0 = ( attrs.pop(10), attrs.pop(20) )
    p1 = None
    if 11 in attrs:
        if 31 in attrs:
            p1 = ( attrs.pop(11), attrs.pop(21), attrs.pop(31) )
        else:
            p1 = ( attrs.pop(11), attrs.pop(21) )
    if 39 in attrs:
        thickness = attrs.pop(39)
    #if 40 in attrs:
    #    radius = attrs.pop(40)

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
            stylestr = attrs.pop(6)
            if stylestr in types:
                style.update(types[stylestr])
                #style["ewmapa:kod_znakowy"] = stylestr
            else:
                sys.stderr.write("Unknown style " + str(stylestr) +
                        " for line " + repr(attrs) +
                        " at line " + str(lnum) + "\n")
                attrs["note"] = "unknown style " + str(stylestr)
        elif 2 in attrs:
            stylestr = attrs.pop(2)
            if stylestr in types:
                style.update(types[stylestr])
                style["ewmapa:kod_znakowy"] = stylestr
            else:
                sys.stderr.write("Unknown style " + str(stylestr) +
                        " for line " + repr(attrs) +
                        " at line " + str(lnum) + "\n")
                attrs["note"] = "unknown style " + str(stylestr)
        else:
            #sys.stderr.write("No style information for line " + repr(attrs) +
            #        " at line " + str(lnum) + "\n")
            #attrs["note"] = "no style information"
            pass
        attrs.update(style)
        if etype != "LINE":
            attrs["geometry"] = etype.lower()
            if 40 in attrs:
                attrs["radius"] = attrs.pop(40)
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
    else:
        sys.stderr.write("Unknown entity type " + etype +
                " at line " + str(lnum) + "\n")
        return

    arr = points
    if p1:
        arr = segments
    if layer not in arr:
        arr[layer] = []

    attrs["_p0"] = p0[0] + "x" + p0[1]
    if p1:
        attrs["_p1"] = p1[0] + "x" + p1[1]
        attrs["_seglyr"] = layer

    arr[layer].append(attrs)

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
    if "EADOD_T_0" not in arr:
        continue
    for attrs in arr.pop("EADOD_T_0"):
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
    if "EADTD_T_0" not in arr:
        continue
    for attrs in arr["EADTD_T_0"]:
        if "_name" not in attrs:
            continue
        a = float(attrs.pop("_text_rotation"))
        p0 = attrs["_p0"].split("x")
        p0 = ( float(p0[0]), float(p0[1]) )
        if "_p1" in attrs:
            p1 = attrs["_p1"].split("x")
            p1 = ( float(p1[0]), float(p1[1]) )
            p0 = ( (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 )
        mindist = 800 # 0.8km in parallel axis
        street = None
        for sp, sa, sname in streets:
            adiff = sa - a
            while adiff > 300.0:
                adiff -= 360.0
            while adiff < -100.0:
                adiff += 360.0
            if (adiff > 15.0 or adiff < -15.0) and \
                    (adiff < 180 - 15.0 or adiff > 180 + 15.0):
                continue

            rad = math.radians(sa)
            per_dist = (sp[0] - p0[0]) * math.sin(rad) - \
                    (sp[1] - p0[1]) * math.cos(rad)
            if (adiff - 90.0) * per_dist > 0.0:
                # Wrong side of the street
                continue

            par_dist = (sp[0] - p0[0]) * -math.cos(rad) - \
                    (sp[1] - p0[1]) * math.sin(rad)
            if abs(par_dist) < mindist and \
                    abs(per_dist) < 150: # 150m perpendicular distance
                mindist = abs(par_dist)
                street = sname
        if street is not None:
            attrs["addr:street"] = street
        attrs["addr:housenumber"] = attrs.pop("_name").lower()

sys.stderr.write("Fixing up building attributes...\n")

for arr in [ segments, points ]:
    # TODO: powinnismy rozroznic miedzy numerem nawyzszej kondygnacji i
    # liczba kondygnacji
    for layer in arr:
        if layer[:5] not in [ "EBUOA", "EBTOO" ]:
            continue
        for attrs in arr[layer]:
            if "_name" not in attrs:
                continue
            t = attrs.pop("_name").lower()
            #attrs["ewmapa:funkcja"] = t
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
                attrs['fixme2'] = 'unknown function ' + str(t)
            attrs.update(levels_attrs)

sys.stderr.write("Building a segment index...\n")

idx = {}
bbox = [ 100000000, 100000000, 0, 0 ]
for layer in segments:
    for seg in segments[layer]:
        p = seg["_p1"].split("x")
        p = ( float(p[0]), float(p[1]) )
        seg['_p1f'] = p
        p = seg["_p0"].split("x")
        p = ( float(p[0]), float(p[1]) )
        seg['_p0f'] = p
        if p[0] < bbox[0]:
            bbox[0] = p[0]
        if p[1] < bbox[1]:
            bbox[1] = p[1]
        if p[0] > bbox[2]:
            bbox[2] = p[0]
        if p[1] > bbox[3]:
            bbox[3] = p[1]
bbox = [ bbox[0] - 10, bbox[1] - 10, bbox[2] + 10, bbox[3] + 10 ]

xsize, ysize = 20, 20 # 20m x 20m
yres = int((bbox[2] - bbox[0] + 200) / xsize)
def add_seg_to_idx(seg):
    p = seg["_p0f"]
    x0 = int((p[0] - xsize * 0.5 - bbox[0]) / xsize)
    x1 = int((p[0] + xsize * 0.5 - bbox[0]) / xsize)
    y0 = int((p[1] - ysize * 0.5 - bbox[1]) / ysize)
    y1 = int((p[1] + ysize * 0.5 - bbox[1]) / ysize)
    if x0 + y0 * yres not in idx:
        idx[x0 + y0 * yres] = []
    idx[x0 + y0 * yres].append(seg)
    if x0 + y1 * yres not in idx:
        idx[x0 + y1 * yres] = []
    idx[x0 + y1 * yres].append(seg)
    if x1 + y0 * yres not in idx:
        idx[x1 + y0 * yres] = []
    idx[x1 + y0 * yres].append(seg)
    if x1 + y1 * yres not in idx:
        idx[x1 + y1 * yres] = []
    idx[x1 + y1 * yres].append(seg)
for layer in segments:
    for seg in segments[layer]:
        add_seg_to_idx(seg)

sys.stderr.write("Merging close nodes and segments...\n")

epsilon = 0.05 # 5cm
for layer in segments:
    toappend = []
    for seg in segments[layer]:
        for pn in [ '_p0f', '_p1f' ]:
            p = seg[pn]
            x = int((p[0] - bbox[0]) / xsize)
            y = int((p[1] - bbox[1]) / ysize)
            j = x + y * yres
            if j not in idx:
                continue
            for seg2 in idx[j]:
                if seg is seg2:
                    continue
                a, b = seg2['_p0f'], seg2['_p1f']
                ab_dist = math.hypot(a[0] - b[0], a[1] - b[1])
                ap_dist = math.hypot(a[0] - p[0], a[1] - p[1])
                bp_dist = math.hypot(b[0] - p[0], b[1] - p[1])
                if ap_dist > ab_dist - epsilon / 2:
                    continue
                if bp_dist > ab_dist - epsilon / 2:
                    continue
                line_dist = abs((p[0] - a[0]) * (b[1] - a[1]) -
                        (p[1] - a[1]) * (b[0] - a[0])) / ab_dist
                if line_dist > epsilon:
                    continue
                newseg = {}
                newseg.update(seg2)
                seg2['_p1'] = seg[pn[:3]]
                newseg['_p0'] = seg[pn[:3]]
                seg2['_p1f'] = p
                newseg['_p0f'] = p

                toappend.append(newseg)
                add_seg_to_idx(newseg)
    #segments[layer] += toappend
    for seg in toappend:
        segments[seg['_seglyr']].append(seg)

idx = None

sys.stderr.write("Removing overlapping segments...\n")

segs = {}
for layer in segments:
    i = 0
    while i < len(segments[layer]):
        s = segments[layer][i]
        idx = s["_p0"] + 'x' + s["_p1"]
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
                if len(poly) > 3:
                    finalnodes[node] = {}
                seg2[ndir] = 0
            if len(poly) > 3:
                nd = [ node for s, n, node in poly ]
                finalways[",".join(sorted(nd))] = {
                    "nd": nd + [ nd[0] ],
                    "attrs": seg,
                }
if 0:
    finalnodes = {}
    finalways = {}
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

idx = {}
bbox = [ 100000000, 100000000, 0, 0 ]
for n in finalnodes:
    p = n.split("x")
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

xsize, ysize = 100, 100 # 100m x 100m
yres = int((bbox[2] - bbox[0] + 200) / xsize)
for w in finalways:
    nd = finalways[w]['nd']
    floatnd = [ ( float(p[0]), float(p[1]) ) for p in \
            [ p.split('x') for p in nd ] ]
    p = floatnd[0]
    finalways[w]['floatnd'] = floatnd
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
        if layers[layer]['type'] != 'attrib':
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
                p.append(p1)
                p0 = ( (p0[0] + p1[0]) * 0.5, (p0[1] + p1[1]) * 0.5 )
                p.append(p0)

            poly = None
            x = int((p0[0] - bbox[0]) / xsize)
            y = int((p0[1] - bbox[1]) / ysize)
            j = x + y * yres
            for pt in p:
                if j not in idx:
                    continue
                for i in idx[j]:
                    nd = finalways[i]["nd"]
                    floatnd = finalways[i]["floatnd"]
                    if nd[0] == nd[-1] and point_in_poly(pt, floatnd):
                        poly = i
                        #print("we determined " + repr(pt) + " is in " +
                        #        repr(nd))
                        break
                if poly:
                    break
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
        attrs['note3'] = 'Conflicting tags: ' + str(list(conflicts.keys()))

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

    node = ElementTree.SubElement(root, "way", {
        "version": str(1),
        "id": way["id"] })

    if 'source' not in way["attrs"]:
        way["attrs"]['source'] = sourcestr

    for prop in way["attrs"]:
        if type(prop) != str:# or prop[0] == "_":
            continue
        ElementTree.SubElement(node, "tag",
                { "k": prop, "v": str(way["attrs"][prop]) })

    for nd in way["nd"]:
        ElementTree.SubElement(node, "nd", { "ref": finalnodes[nd]["_id"] })
finalnodes = None
finalways = None

sys.stderr.write("Writing to file...\n")

ElementTree.ElementTree(root).write("budynki.osm", "utf-8")
