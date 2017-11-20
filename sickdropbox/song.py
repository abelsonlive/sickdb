import gevent.monkey; gevent.monkey.patch_all()
import gevent
import os
import tempfile
import json
import hashlib
import sys

import requests
import taglib

from sickdropbox import util
from sickdropbox import settings

class Song(object):

  def __init__(self, file):
    self.file = file
    self.attrs = {}
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
      self.attrs["tags"]["artist"] = self.id3.tags.get("ARTIST", [""])[0]
      self.attrs["tags"]["title"] = self.id3.tags.get("TITLE", [""])[0]
      self.attrs["tags"]["album"] = self.id3.tags.get("TITLE", [""])[0]
      self.attrs["tags"]["date"] = self.id3.tags.get("DATE", [""])[0]
      self.attrs["tags"]["genre"] = self.id3.tags.get("GENRE", [""])[0]
      self.attrs["tags"]["bpm"] = self.id3.tags.get("BPM", [""])[0]
      self.attrs["tags"]["tracknumber"] = self.id3.tags.get("TRACKNUMBER", [""])[0]
      raw_key = self.id3.tags.get("INITIALKEY", [""])[0]
      self.attrs["tags"]["initialkey"] = settings.HARMONIC_TO_KEY.get(raw_key, settings.KEY_LOOKUP.get(raw_key, ""))

  def get_fingerprint(self):
    """
    Extract uid and fingerprint via
    """
    if self.attrs.get("fingerprint", None) is None:
      cmd = '{0} "{1}" -json'.format(settings.FP_CALC_PATH, self.file)
      p = util.sys_exec(cmd)
      if not p.ok:
        sys.stderr.write("WARNING: Error running {0}: {1}\n".format(cmd, p.stdout))
      data = json.loads(p.stdout)
      data["duration"] = str(int(round(data.get("duration", 0), 0)))
      data["uid"] = hashlib.md5(data.get("fingerprint", "").encode("utf-8")).hexdigest()
      self.attrs.update(data)

  def get_bpm_and_key(self):
    """
    """
    if self.attrs.get("bpm", None) is None:
      # make temp file root
      fp_root = tempfile.mktemp(suffix='analysis-output')

      # cmd
      cmd = '{0} "{1}" "{2}"'.format(settings.FREESOUND_PATH, self.file, fp_root)

      # exec
      proc = util.sys_exec(cmd)
      if not proc.ok:
        raise Exception("Error running: {0}\n{1}".format(cmd, proc.stdout))

      # grab output file
      fp_stats = fp_root + "_statistics.json"
      fp_frames = fp_root + "_frames.json"
      data = json.load(open(fp_stats))

      # remove
      try:
        os.remove(fp_stats)
        os.remove(fp_frames)
      except:
        pass

      self.attrs["bpm"] = str(round(data.get("rhythm",{}).get("bpm", settings.DEFAULT_BPM), 1))
      self.attrs["key"] = settings.KEY_LOOKUP.get((data.get("tonal", {}).get("key_key", "") + data.get("tonal", {}).get("key_scale", "")).upper(), settings.DEFAULT_KEY)
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
        sys.stderr.write("WARNING: Could not resolve {0} with musicbrainz because: {1}\n".format(self.file, res["error"]["message"]))
      res = res.get("results", [])
      if not len(res):
        sys.stderr.write("WARNING: Could not find Musicbrainz info for {0}\n".format(self.file))
        rec = {}

      else:
        res = res[0].get("recordings", [])
        if not len(res):
          sys.stderr.write("WARNING: Could not find Musicbrainz info for {0}\n".format(self.file))
        else:
          rec = res[0]

      # update attributes
      self.attrs["musicbrainz"].update({
        "id": rec.get("id", ""),
        "title": rec.get("title", ""),
        "artist": rec.get("artists", [{}])[0].get("name", ""),
        "artist_id": rec.get("artists", [{}])[0].get("id", ""),
      })

  def analyze(self):
    self.get_file()
    self.get_id3_tags()
    self.get_fingerprint()
    self.get_music_brainz()
    self.get_bpm_and_key()

  def set_id3_tag(self, tag, value):
    """
    Set an ID3 Tag
    """
    if not isinstance(value, list):
      value = [value]
    value  = list(map(str, value))
    self.id3.tags[tag.upper()] = value

  def save_id3_tags(self):
    """
    Save ID3 Tags
    """
    self.id3.save()


def run():
  import sys
  file = sys.argv[1]
  s = Song(file)
  s.analyze()
  print(json.dumps(s.attrs))
