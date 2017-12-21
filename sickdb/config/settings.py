import os

ENV = os.getenv('SICKDB_ENV')

if not ENV:
    raise RuntimeError("No SICKDB_ENV supplied.")

# if ENV == 'prod':
#     from config.prod import *

if ENV == 'dev':
    from sickdb.config.dev import *

# if ENV == 'test':
#     from config.test import *


FSM = [
    'update',
    'dedupe',
    'to_itunes'
]


# Lookup of Raw Essentia Key to Simplified
KEY_LOOKUP = {
    "AMAJOR": "A",
    "AMINOR": "Am",
    "A#MAJOR": "Bb",
    "A#MINOR": "Bbm",
    "BBMAJOR": "Bb",
    "BBMINOR": "Bbm",
    "BMAJOR": "B",
    "BMINOR": "Bm",
    "CMAJOR": "C",
    "CMINOR": "Cm",
    "C#MAJOR": "Db",
    "C#MINOR": "Dbm",
    "DBMAJOR": "Db",
    "DBMINOR": "Dbm",
    "DMAJOR": "D",
    "DMINOR": "Dm",
    "D#MAJOR": "Eb",
    "D#MINOR": "Ebm",
    "EBMAJOR": "Eb",
    "EBMINOR": "Ebm",
    "EMAJOR": "E",
    "EMINOR": "Em",
    "FMAJOR": "F",
    "FMINOR": "Fm",
    "F#MAJOR": "F#",
    "F#MINOR": "F#m",
    "GBMAJOR": "F#",
    "GBMINOR": "F#m",
    "GMAJOR": "G",
    "GMINOR": "Gm",
    "G#MAJOR": "Ab",
    "G#MINOR": "Abm",
    "ABMAJOR": "Ab",
    "ABMINOR": "Abm",
    ###
    "AMAJ": "A",
    "AMIN": "Am",
    "A#MAJ": "Bb",
    "A#MIN": "Bbm",
    "BBMAJ": "Bb",
    "BBMIN": "Bbm",
    "BMAJ": "B",
    "BMIN": "Bm",
    "CMAJ": "C",
    "CMIN": "Cm",
    "C#MAJ": "Db",
    "C#MIN": "Dbm",
    "DBMAJ": "Db",
    "DBMIN": "Dbm",
    "DMAJ": "D",
    "DMIN": "Dm",
    "D#MAJ": "Eb",
    "D#MIN": "Ebm",
    "EBMAJ": "Eb",
    "EBMIN": "Ebm",
    "EMAJ": "E",
    "EMIN": "Em",
    "FMAJ": "F",
    "FMIN": "Fm",
    "F#MAJ": "F#",
    "F#MIN": "F#m",
    "GBMAJ": "F#",
    "GBMIN": "F#m",
    "GMAJ": "G",
    "GMIN": "Gm",
    "G#MAJ": "Ab",
    "G#MIN": "Abm",
    "ABMAJ": "Ab",
    "ABMIN": "Abm",
    ###
    "A": "A",
    "AM": "Am",
    "BB": "Bb",
    "BBM": "Bbm",
    "BB": "Bb",
    "BBM": "Bbm",
    "B": "B",
    "BM": "Bm",
    "C": "C",
    "CM": "Cm",
    "DB": "Db",
    "DBM": "Dbm",
    "DB": "Db",
    "DBM": "Dbm",
    "D": "D",
    "DM": "Dm",
    "EB": "Eb",
    "EBM": "Ebm",
    "EB": "Eb",
    "EBM": "Ebm",
    "E": "E",
    "EM": "Em",
    "F": "F",
    "FM": "Fm",
    "F#": "F#",
    "F#M": "F#m",
    "F#": "F#",
    "F#M": "F#m",
    "G": "G",
    "GM": "Gm",
    "AB": "Ab",
    "ABM": "Abm",
    "AB": "Ab",
    "ABM": "Abm"
}

HARMONIC_TO_KEY = {
    "1A": "Abm",
    "2A": "Ebm",
    "3A": "Bbm",
    "4A": "Fm",
    "5A": "Cm",
    "6A": "Gm",
    "7A": "Dm",
    "8A": "Am",
    "9A": "Em",
    "10A": "Bm",
    "11A": "F#m",
    "12A": "Dbm",
    "1B": "B",
    "2B": "F#",
    "3B": "Db",
    "4B": "Ab",
    "5B": "Eb",
    "6B": "Bb",
    "7B": "F",
    "8B": "C",
    "9B": "G",
    "10B": "D",
    "11B": "A",
    "12B": "E"
}

KEY_TO_HARMONIC = {value: key for key, value in HARMONIC_TO_KEY.items()}
