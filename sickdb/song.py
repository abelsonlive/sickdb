import os
import tempfile
import json
import hashlib
import sys
import pipes

import requests
import taglib
from unidecode import unidecode

from sickdb import util
from sickdb import settings

class Song(object):

  def __init__(self, file):
    self.file = file
    self.attrs = {}
    self.truth = {}
    self.attrs["type"] = util.path_get_ext(file)
    self.attrs["tags"] = {}
    self.attrs["file"] = {}
    self.attrs["musicbrainz"] = {}

  def get_file(self):
    if self.attrs["file"].get("title", None) is None:
      m = settings.RE_FILEPATH.search(self.file)
      if m:
        d = m.groupdict()
      else:
        d = {}
      self.attrs["file"]["artist"] = d.get("artist", "")
      self.attrs["file"]["album"] = d.get("album", "")
      self.attrs["file"]["path"] = d.get("path", "")

      m = settings.RE_FILEMETA.search(self.attrs["file"]["path"])
      if m:
        d = m.groupdict()
      else:
        d = {}
      self.attrs["file"]["bpm"] = d.get("bpm", "")
      self.attrs["file"]["key"] = d.get("key", "")
      self.attrs["file"]["uid"] = d.get("uid", "")
      self.attrs["file"]["type"] = d.get("type", "")
      self.attrs["file"]["title"] = d.get("title", "")

  def is_valid(self):
    """
    Is this a valid file
    """
    return self.attrs["type"] in settings.VALID_TYPES

  def get_id3_tags(self):
    """
    Get ID3 Tags
    """
    if self.attrs["tags"].get("bit_rate", None) is None:
      self.id3 = taglib.File(self.file)
      self.attrs["tags"]["bit_rate"] = self.id3.bitrate
      self.attrs["tags"]["path"] = self.id3.path
      self.attrs["tags"]["sample_rate"] = self.id3.sampleRate
      self.attrs["tags"]["channels"] = self.id3.channels
      self.attrs["tags"]["artist"] = util.std_string(util.unlistify(self.id3.tags.get("ARTIST", "")))
      self.attrs["tags"]["title"] = util.std_string(util.unlistify(self.id3.tags.get("TITLE", "")))
      self.attrs["tags"]["album"] = util.std_string(util.unlistify(self.id3.tags.get("ALBUM", "")))
      self.attrs["tags"]["date"] = util.std_string(util.unlistify(self.id3.tags.get("DATE", "")))
      self.attrs["tags"]["bpm"] = util.std_string(util.unlistify(self.id3.tags.get("BPM", "")))
      raw_key = util.unlistify(self.id3.tags.get("INITIALKEY", ""))
      self.attrs["tags"]["initialkey"] = settings.HARMONIC_TO_KEY.get(raw_key, settings.KEY_LOOKUP.get(raw_key, ""))

  def get_fingerprint(self):
    """
    Extract uid and fingerprint via
    """
    if self.attrs.get("fingerprint", None) is None:
      cmd = '{0} {1} -json'.format(settings.FP_CALC_PATH, pipes.quote(self.file))
      p = util.sys_exec(cmd)
      if not p.ok:
        sys.stderr.write("WARNING: Error running {0}: {1}\n".format(cmd, p.stderr))
      try:
        data = json.loads(p.stdout)
        data["duration"] = str(int(round(data.get("duration", 0), 0)))
        data["uid"] = hashlib.md5(data.get("fingerprint", "").encode("utf-8")).hexdigest()
        self.attrs.update(data)
      except Exception as e:
        sys.stderr.write("WARNING: Could not compute fingerprint for {0}\n".format(self.file))
        self.attrs.update({"fingerprint":"", "duration": "", "uid": hashlib.md5(self.file.encode("utf-8")).hexdigest()})

  def get_bpm_and_key(self):
    """
    """
    if self.attrs.get("bpm", None) is None:
      # make temp file root
      fp_root = tempfile.mktemp(suffix='analysis-output')

      # cmd
      cmd = '{0} {1} "{2}"'.format(settings.FREESOUND_PATH, pipes.quote(self.file), fp_root)

      # exec
      p = util.sys_exec(cmd)
      if not p.ok:
        sys.stderr.write("Error running: {0}\n{1}\n".format(cmd, p.stderr))
        return
      # grab output file
      try:
        data = json.loads(open(fp_root).read())
      except Exception as e:
          sys.stderr.write("WARNING: Could not decode {0} because: {1}".format(self.file, e))
          return
      # remove
      try:
        os.remove(fp_root)
        os.remove(fp_root)
      except:
        pass

      self.attrs["bpm"] = str(round(data.get("rhythm",{}).get("bpm", settings.DEFAULT_BPM), 1))
      self.attrs["key"] = settings.KEY_LOOKUP.get((data.get("tonal", {}).get("key_temperley", {}).get("key", "") + data.get("tonal", {}).get("key_temperley", {}).get("scale", "")).upper(), settings.DEFAULT_KEY)
      self.attrs["chord"] = settings.KEY_LOOKUP.get((data.get("tonal", {}).get("chords_key", "") + data.get("tonal", {}).get("chords_scale", "")).upper(), settings.DEFAULT_KEY)
      self.attrs["harmonic_key"] = settings.KEY_TO_HARMONIC.get(self.attrs["key"], "")

  def get_music_brainz(self):
    """
    Reconcile song with Music Brainz
    """
    if self.attrs["musicbrainz"].get("id", None) is None:
      self.get_fingerprint()

      # handle requests / errors
      params = {
        "client": settings.ACOUSTID_CLIENT,
        "format": "json",
        "fingerprint": self.attrs["fingerprint"],
        "duration": self.attrs["duration"],
        "meta": "recordings"
      }
      r = requests.get(settings.ACOUSTID_URL, params=params)
      res = r.json()
      if res["status"] == "error":
        sys.stderr.write("WARNING: Could not resolve {0} with Musicbrainz because: {1}\n".format(self.file, res["error"]["message"]))
        rec = {}

      res = res.get("results", [])
      if not len(res):
        sys.stderr.write("WARNING: Could not find Musicbrainz info for {0}\n".format(self.file))
        rec = {}

      else:
        res = res[0].get("recordings", [])
        if not len(res):
          sys.stderr.write("WARNING: Could not find Musicbrainz info for {0}\n".format(self.file))
          rec = {}
        else:
          rec = res[0]

      # update attributes
      self.attrs["musicbrainz"].update({
        "id": rec.get("id", ""),
        "title": rec.get("title", ""),
        "artist": rec.get("artists", [{}])[0].get("name", ""),
        "artist_id": rec.get("artists", [{}])[0].get("id", ""),
      })

  def reconcile(self):
    self.truth = {
      "bpm": settings.DEFAULT_BPM,
      "key": settings.DEFAULT_KEY,
      "artist": settings.DEFAULT_ARTIST,
      "album": settings.DEFAULT_ALBUM,
      "type": self.attrs.get("type"),
      "title": self.attrs["file"].get("title", ""),
      "uid": self.attrs["file"].get("uid", "")
    }

    # analyze UID
    if self.attrs.get("uid"):
      self.truth["uid"] = self.attrs["uid"]

    # analyze BPM
    if self.attrs.get("bpm"):
      self.truth["bpm"] = self.attrs["bpm"].strip()
    elif self.attrs["tags"].get("bpm"):
      self.truth["bpm"] = self.attrs["tags"]["bpm"].strip()

    # analyze KEY
    if self.attrs.get("key"):
      self.truth["key"] = self.attrs["key"]
    elif self.attrs["tags"].get("key"):
      self.truth["key"] = self.attrs["tags"]["key"]

    # analyze ARTIST
    if self.attrs["musicbrainz"].get("artist"):
      self.truth["artist"] = util.std_string(self.attrs["musicbrainz"]["artist"])
    elif self.attrs["tags"].get("artist"):
      self.truth["artist"] = util.std_string(self.attrs["tags"]["artist"])
    elif self.attrs["file"].get("artist"):
      self.truth["artist"] = util.std_string(self.attrs["file"]["artist"])

    # analyze ALBUM
    if self.attrs["tags"].get("album"):
      self.truth["album"] = util.std_string(self.attrs["tags"]["album"].strip())
    elif self.attrs["file"].get("album"):
      self.truth["album"] = util.std_string(self.attrs["file"]["album"].strip())

    # analyze TITLE
    if self.attrs["musicbrainz"].get("title"):
      self.truth["title"] = util.std_string(self.attrs["musicbrainz"]["title"])
    elif self.attrs["tags"].get("title"):
      self.truth["title"] = util.std_string(self.attrs["tags"]["title"])
    elif self.attrs["file"].get("title"):
      self.truth["title"] = util.std_string(self.attrs["file"]["title"])

    # analyze TYPE
    if self.attrs.get("type"):
      self.truth["type"] = self.attrs["type"]
    elif self.attrs["file"].get("type"):
      self.truth["type"] = self.attrs["file"]["type"]

    # format TITLE
    self.truth["title"] = settings.TITLE_FORMAT.format(**self.truth)
    self.truth["directory"] = os.path.join(settings.DIR_FORMAT.format(**self.truth))
    self.truth["file"] = os.path.join(self.truth["directory"], settings.FILE_FORMAT.format(**self.truth))

  def analyze(self):
    """
    Analyze concurrently
    """
    self.get_file()
    self.get_id3_tags()
    self.get_fingerprint()
    self.get_music_brainz()
    self.get_bpm_and_key()
    self.reconcile()

  def update(self):
    self.set_id3_tag("artist", self.truth["artist"])
    self.set_id3_tag("initialkey", self.truth["key"])
    self.set_id3_tag("bpm", self.truth["bpm"])
    self.set_id3_tag("COMMENT:UID", self.truth["uid"])
    self.set_id3_tag("title", self.truth["title"])
    self.save_id3_tags()

  def set_id3_tag(self, tag, value):
    """
    Set an ID3 Tag
    """
    value = util.listify(value)
    value  = list(map(str, value))
    self.id3.tags[tag.upper()] = value

  def save_id3_tags(self):
    """
    Save ID3 Tags
    """
    self.id3.save()

