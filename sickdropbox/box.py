import sys
import os

from sickdropbox import util
from sickdropbox import settings
from sickdropbox.song import Song

class Box(object):

  def __init__(self, directory, cleanup=False):
    self.directory = os.path.expanduser(directory)
    self.cleanup = cleanup
    self.setup()

  def setup(self):
    util.sys_exec('mkdir -p "{0}"'.format(self.directory))
    self.uids = set()
    self.songs = []
    self.duplicates = []
    self.new = []

  @property
  def num_new(self):
    return len(self.new)

  @property
  def num_duplicates(self):
    return len(self.duplicates)

  @property
  def num_loaded(self):
    return len(self.songs)

  def load(self):
    """
    List all songs in the box.
    """
    for fp in util.path_list(self.directory):
      song = Song(fp)
      song.get_file()
      uid = song.attrs['file']['uid']
      if uid:
        if uid not in self.uids:
          self.songs.append(song)
          self.uids.add(uid)
        else:
          self.duplicates.append(song)
      else:
        self.new.append(song)

    sys.stderr.write("INFO: SickDB: {0}\n".format(self.directory))
    sys.stderr.write("\t#imported: {0}\n".format(self.num_loaded))
    sys.stderr.write("\t#duplicates: {0}\n".format(self.num_duplicates))
    sys.stderr.write("\t#new: {0}\n".format(self.num_new))

  def update(self):
    """
    Update new songs
    """
    sys.stderr.write("INFO: Importing {0} files into SickDB {1}\n".format(self.num_new, self.directory))
    for song in self.new:
      song.get_fingerprint()
      if song.attrs["uid"] in self.uids:
        print("INFO: Found Duplicate: {0}".format(song.file))
        self.duplicates.append(song)
      else:
        print(self.import_song(song))

  def import_song(self, song):
    """
    Import and Standardize a Song
    """
    sys.stderr.write("INFO: Analyzing: {0}\n".format(song.file))
    song.get_file()
    truth = {
      "bpm": settings.DEFAULT_BPM,
      "key": settings.DEFAULT_KEY,
      "artist": settings.DEFAULT_ARTIST,
      "album": settings.DEFAULT_ALBUM,
      "type": song.attrs.get("type"),
      "title": song.attrs["file"].get("title", ""),
      "uid": song.attrs["file"].get("uid", "")
    }
    song.analyze()

    # analyze UID
    if song.attrs.get("uid"):
      truth["uid"] = song.attrs["uid"]
    song.set_id3_tag("COMMENT:UID", truth["uid"])

    # analyze BPM
    if song.attrs.get("bpm"):
      truth["bpm"] = song.attrs["bpm"]
    elif song.attrs["tags"].get("bpm"):
      truth["bpm"] = song.attrs["tags"]["bpm"]
    song.set_id3_tag("bpm", truth["bpm"])

    # analyze KEY
    if song.attrs.get("key"):
      truth["key"] = song.attrs["key"]
    elif song.attrs["tags"].get("key"):
      truth["key"] = song["tags"]["key"]
    song.set_id3_tag("initialkey", truth["key"])

    # analyze ARTIST
    if song.attrs["musicbrainz"].get("artist"):
      truth["artist"] = song.attrs["musicbrainz"]["artist"]
    elif song.attrs["tags"].get("artist"):
      truth["artist"] = song.attrs["tags"]["artist"]
    elif song.attrs["file"].get("artist"):
      truth["artist"] = song.attrs["file"]["artist"]
    song.set_id3_tag("artist", truth["artist"])

    # analyze ALBUM
    if song.attrs["tags"].get("album"):
      truth["album"] = song.attrs["tags"]["album"]
    elif song.attrs["file"].get("album"):
      truth["album"] = song.attrs["file"]["album"]
    song.set_id3_tag("album", truth["album"])

    # analyze TITLE
    if song.attrs["musicbrainz"].get("title"):
      truth["title"] = song.attrs["musicbrainz"]["title"]
    elif song.attrs["tags"].get("title"):
      truth["title"] = song.attrs["tags"]["title"]
    elif song.attrs["file"].get("title"):
      truth["title"] = song.attrs["file"]["title"]

    # analyze TYPE
    if song.attrs.get("type"):
      truth["type"] = song.attrs["type"]
    elif song.attrs["file"].get("type"):
      truth["type"] = song.attrs["file"]["type"]

    # format TITLE
    truth["title"] = settings.TITLE_FORMAT.format(**truth)
    truth["directory"] = os.path.join(self.directory, settings.DIR_FORMAT.format(**truth))
    truth["file"] = os.path.join(truth["directory"], settings.FILE_FORMAT.format(**truth))
    song.set_id3_tag("title", truth["title"])
    song.save_id3_tags()

    # standardize file naming
    if song.file != truth["file"]:
      p = util.sys_exec('mkdir -p "{0}"'.format(truth["directory"]))
      if not p.ok:
        raise Exception("ERROR: Could not copy file from {0} to {1} because {2}".format(song.file, truth["file"], p.stdout))
      sys.stderr.write("INFO: Copying {0} -> {1}".format(song.file, truth["file"]))
      p = util.sys_exec('cp "{0}" "{1}"'.format(song.file, truth["file"]))
      if not p.ok:
        raise Exception("ERROR: Could not copy file from {0} to {1} because {2}".format(song.file, truth["file"], p.stdout))

      if self.cleanup:
        os.remove(song.file)

  def dedupe(self):
    for song in self.duplicates:
      sys.stderr.write("INFO: Removing Duplicate: {0}\n".format(song.file))
      os.remove(song.file)

def run():
  d = sys.argv[1]
  b = Box(d, cleanup=True)
  b.load()
  b.update()
  b.dedupe()
  # print("Imported:")
  # print([s.attrs for s in b.songs])
  # print("Duplicates:")
  # print([s.attrs for s in b.duplicates])
  # print("New:")
  # print([s.attrs for s in b.new])
  # print("Imported IDs:")
  # print(list(b.uids))