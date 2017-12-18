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
sickdb-update /path/to/music
```

## Add to iTunes

Change the `ADD_TO_ITUNES_PATH` value in `settings.py` to the path where your `Automatically\ Add\ to\ iTunes.localized` file resides.

This might default to:

```
/Users/<user>/Music/iTunes/iTunes\ Media/Automatically\ Add\ to\ iTunes.localized/
```

Then re-install sickdb:

```
make build
```

```
sickdb-to-itunes /path/to/music
```