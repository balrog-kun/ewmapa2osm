#! /usr/bin/python3
# vim: fileencoding=utf-8 encoding=utf-8 et sw=4
# BSD license, 2011 Andrzej Zaborowski

filename = 'rudaslaska.dxf'
sourcestr = 'UM Ruda Śląska'
encoding = 'cp1250'
road_labels = 'EADOD_T_0'
housenumber_labels = 'EADTD_T_0'

layers = {
    "EADOD_T_0": {
        "type": "text",
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
    "EBUPP_L_4": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_5": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_6": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_7": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_8": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_9": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_10": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
    },
    "EBUPP_L_11": {
        "type": "spatial",
        "name": "Nieudokumentowana warstwa, do sprawdzenia",
        "use": 1,
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
