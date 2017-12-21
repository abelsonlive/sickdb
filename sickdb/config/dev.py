import os
import re
from sickdb import util

ACOUSTID_URL = 'https://api.acoustid.org/v2/lookup'
TITLE_FORMAT = "{bpm} ({key}) {title}"
FILE_FORMAT = "{title}|{uid}.{type}"
DIR_FORMAT = "{artist}/{album}"
RE_FILEPATH = re.compile(
    "^.*/(?P<artist>[^/]+)/(?P<album>[^/]+)/(?P<path>.*)$")
RE_FILEMETA = re.compile(
    "^((?P<bpm>[0-9\.]+) \((?P<key>[A-Za-z]{1,3})\) )?(?P<title>[^\|]+)(\|)?(?P<uid>[A-Za-z0-9]+)?\.(?P<type>[a-z0-9]+)$")
DEFAULT_ARTIST = "Unknown Artist"
DEFAULT_ALBUM = "Unknown Album"
DEFAULT_BPM = "0"
DEFAULT_KEY = ""
VALID_TYPES = ['mp3', 'aiff', 'wav', 'flac', 'm4a', 'ogg']
ADD_TO_ITUNES_PATH = '/Volumes/db/Music/Automatically Add to iTunes.localized'
ACOUSTID_CLIENT = os.getenv("SICKDROPBOX_ACOUSTID_CLIENT")
FP_CALC_PATH = util.path_here(__file__, 'bin/chromaprint-fpcalc')
FREESOUND_PATH = util.path_here(__file__, 'bin/essentia-freesound')
S3_BUCKET = os.getenv("SICKDB_S3_BUCKET")
S3_PATH_KEY = os.getenv("SICKDB_S3_PATH_KEY")
