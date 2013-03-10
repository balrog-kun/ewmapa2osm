#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# BSD license, 2011 Andrzej Zaborowski

filename = 'BUDYNKI/bud+adr_bedzin.dxf'
sourcestr = 'PODGIK Będzin'
encoding = 'latin2'
road_labels = 'GSLOUL_O'
housenumber_labels = 'GEPADR_O'

types = {
    "CONTINUOUS": {},
}

layers = {
    "GSLOUL_O": {
        "type": "text",
        "name": "Nazwa ulicy, placu, miejscowości",
        "use": 1,
    },
    "GEPADR_O": {
        "type": "attrib",
        "name": "Numer adresowy",
        "use": 1,
    },
    "GESBZO_O": {
        "type": "attrib",
        "name": "Funkcja, numer najwyzszej kondygnacji",
        "use": 1,
    },
    "GESBZO": {
        "type": "spatial",
        "name": "Przyziemie budynku",
        "use": 1,
        "default": { "building": "yes" },
    },
}
