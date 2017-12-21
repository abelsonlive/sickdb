# Sick Dropbox

Automatically analyze and dedupe a directory of tunes.

# Pre-reqs

```
pipenv
essentia essentia_streaming_extractor_freesounds binary
```


## For Mac:

For now getting the required essentia binary requires compiling essentia locally and then copying the file over to the sickdb bin directory.

```
git clone https://github.com/MTG/essentia
cd essentia
./waf configure --mode=release --build-static --with-examples
./waf install
cp build/src/examples/essentia_streaming_extractor_freesound /path/to/sickdb/sickdb/bin/essentia-freesound
```


Then copy this binary to the sick db bin folder:

```

```


# Installation (on a Mac)

```
pipenv install
pipenv shell
make build
```

You currently need this environment variable:

```
export SICKDROPBOX_ACOUSTID_CLIENT=<key>
```

# Utilities

## Update

Run track analysis and transformations on a directory of audio files:

```
sickdb-update -d /path/to/music
```

## Add to iTunes

Add an `ADD_TO_ITUNES_PATH` environment variable for the location where your `Automatically\ Add\ to\ iTunes.localized` file resides.

This might default to:

```
export ADD_TO_ITUNES_PATH=/Users/<user>/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes.localized/
```

Then re-install sickdb:

```
make build
```

```
sickdb-to-itunes d /path/to/music
```

## Dedupe

Dedupe the audio files in a directory.

```
sickdb-dedupe -d /path/to/music
```


## FSM

You can run the hard-wired sickdb 'finite state machine' with all steps:

```
sickdb -d /path/to/music
```

Or just some steps:

```
sickdb -d /path/to/music --dedupe --to-itunes
```

## Sync

Set environment variables for `SICKDB_S3_BUCKET` and `SICKDB_S3_PATH_KEY`. If you want a file to show up at `s3://sickdb/dev/songs/cool-song.mp3`, then set:

```
export SICKDB_S3_BUCKET=sickdb
export SICKDB_S3_PATH_KEY=dev/songs
```

Then local files will upload to s3 via:

```
sickdb-sync -d /path/to/music/
```