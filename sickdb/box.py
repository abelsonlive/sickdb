import sys
import os
import pipes
import shutil
from multiprocessing import Pool

from sickdb import util
from sickdb import settings
from sickdb.song import Song

class Box(object):

  def __init__(self, directory, cleanup=False, num_workers=8):
    self.directory = os.path.expanduser(directory)
    if not self.directory.endswith("/"):
      self.directory += "/"
    self.cleanup = cleanup
    self.num_workers = num_workers
    self.setup()

  def setup(self):
    util.sys_exec('mkdir -p "{0}"'.format(self.directory))

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
    self.uids = set()
    self.songs = []
    self.duplicates = []
    self.new = []
    for fp in util.path_list(self.directory):
      song = Song(fp)
      song.get_file()
      if song.is_valid():
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

  def update_song(self, song):
    """
    """
    song.get_fingerprint()
    if song.attrs["uid"] in self.uids:
      print("INFO: Found Duplicate: {0}".format(song.file))
      self.duplicates.append(song)
    else:
      self.import_song(song)

  def import_song(self, song):
    """
    Import and Standardize a Song
    """
    sys.stderr.write("INFO: Analyzing: {0}\n".format(song.file))
    song.get_file()
    song.analyze()
    song.update()

    # standardize file naming
    truth_file = os.path.join(self.directory, song.truth["file"]).replace('//', '/')
    if song.file != truth_file:
      p = util.sys_exec('mkdir -p "{0}"'.format(self.directory + song.truth["directory"]))
      if not p.ok:
        sys.stderr.write("ERROR: Could not copy file from {0} to {1} because {2}\n".format(song.file, truth_file, p.stdout))
      sys.stderr.write("INFO: Copying {0} -> {1}\n".format(song.file, truth_file))
      try:
        shutil.copy(song.file, truth_file)
      except Exception as e:
        sys.stderr.write("ERROR: Could not copy file from {0} to {1} becauce {2}\n".format(song.file, truth_file, e))
      # delete source file
      if self.cleanup:
        os.remove(song.file)

  def update(self):
    """
    Update new songs
    """
    self.load()
    sys.stderr.write("INFO: Importing {0} files into SickDB {1}\n".format(self.num_new, self.directory))
    with Pool(self.num_workers) as p:
      p.map(self.update_song, self.new)

  def dedupe(self):
    """
    Remove duplicates
    """
    self.load()
    sys.stderr.write("INFO: Deduping {0} files from SickDB {1}\n".format(self.num_duplicates, self.directory))
    for song in self.duplicates:
      sys.stderr.write("INFO: Removing Duplicate: {0}\n".format(song.file))
      try:
        os.remove(song.file)
      except:
        pass
    self.cleanup_dirs()

  def cleanup_dirs(self):
    """
    Remove empty subdirectories
    """
    for fp in os.walk(self.directory):
      d = fp[0]
      if os.path.isdir(d):
        if not os.listdir(d):
          sys.stderr.write("INFO: Removing directory {0}\n".format(d))
          try:
            os.rmdir(d)
          except:
            pass

  def add_to_itunes(self):
    self.load()
    for s in self.songs:
      util.sys_exec("mv {0} '{1}'".format(pipes.quote(s.file), settings.ADD_TO_ITUNES_PATH))


def run_update():
  d = sys.argv[1]
  b = Box(d, cleanup=True)
  b.update()

def run_dedupe():
  d = sys.argv[1]
  b = Box(d, cleanup=True)
  b.dedupe()

def run_to_itunes():
  d = sys.argv[1]
  b = Box(d, cleanup=True)
  b.add_to_itunes()

