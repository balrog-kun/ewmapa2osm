#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# BSD license, 2011 Andrzej Zaborowski

filename = '25_2013.dxf'
sourcestr = 'PODGIK Gorzów'
encoding = 'cp1250'
road_labels = 'EAD_T_2'
housenumber_labels = 'EAD_T_1'

layers = {
    "EAD_T_1": {
        "type": "attrib",
        "name": "Numer adresowy",
        "use": 1,
    },
    "EAD_T_2": {
        "type": "text",
        "name": "Nazwa ulicy, placu, miejscowości",
        "use": 1,
    },
    "EBU_T_0": {
        "type": "attrib-point",
        "name": "Symbole budynków",
        "use": 1,
    },
    "EBU_T_1": {
        "type": "attrib-point",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "T1" },
    },
    "EBU_T_2": {
        "type": "attrib-point",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "T2" },
    },
    "EBU_T_3": {
        "type": "attrib",
        "name": "Funkcja, numer najwyzszej kondygnacji budynku",
        "use": 1,
        "default": { "building": "yes" },
    },
    "EBU_T_4": {
        "type": "attrib",
        "name": "Numer elementu w zespole budynków?",
        "use": 0,
    },
    "EBU_T_5": {
        "type": "attrib-point",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "T5" },
    },
    "EBU_T_6": {
        "type": "attrib-point",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "T6" },
    },
    "EBU_T_7": {
        "type": "attrib-point",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "T7" },
    },
    "EBU_L_0": {
        "type": "spatial",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "L0" },
    },
    "EBU_L_1": {
        "type": "spatial",
        "name": "Przyziemie lub obrys budynku",
        "use": 1,
        "default": { "building": "yes" },
    },
    "EBU_L_2": {
        "type": "spatial",
        "name": "Obrys ruiny",
        "use": 1,
        "default": {},
    },
    "EBU_L_3": {
        "type": "spatial",
        "name": "Fragment budynku bez numerka",
        "use": 1,
        "default": { "building": "yes" },
    },
    "EBU_L_4": {
        "type": "spatial",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "L4" },
    },
    "EBU_L_5": {
        "type": "spatial",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "L5" },
    },
    "EBU_L_6": {
        "type": "spatial",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "L6" },
    },
    "EBU_L_7": {
        "type": "spatial",
        "name": "Nieznana warstwa",
        "use": 1,
        "default": { "fixme": "L7" },
    },
}
