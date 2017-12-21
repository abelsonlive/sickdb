import sys
import argparse
from functools import wraps

from sickdb.box import Box
from sickdb.config.settings import FSM


def process_args(args):
    arg_parser = argparse.ArgumentParser(description="Sick Dflat")
    arg_parser.add_argument('-d', '--dir', dest='directory',
                            help='The path to a directory of music files.')
    arg_parser.add_argument(
        '-u', '--update', dest='update', action='store_true', help='Update files.')
    arg_parser.add_argument(
        '-dd', '--dedupe', dest='dedupe', action='store_true', help='Dedupe files.')
    arg_parser.add_argument(
        '-t', '--to-itunes', dest='to_itunes', action='store_true', help='Add files to iTunes.')

    return vars(arg_parser.parse_args(args))


def preload_args(cli_args):

    def _preload_args(f):

        @wraps(f)
        def _run(*args, **kwargs):
            if not len(kwargs):
                kwargs = process_args(cli_args)
            return f(*args, **kwargs)

        return _run
    return _preload_args


@preload_args(sys.argv[1:])
def run_update(directory=None, **kwargs):
    Box(directory, cleanup=True).update()


@preload_args(sys.argv[1:])
def run_dedupe(directory=None, **kwargs):
    Box(directory, cleanup=True).dedupe()


@preload_args(sys.argv[1:])
def run_to_itunes(directory=None, **kwargs):
    Box(directory, cleanup=True).add_to_itunes()


def main(args=sys.argv[1:]):
    kwargs = process_args(args)
    runs = dict(update=run_update,
                dedupe=run_dedupe,
                to_itunes=run_to_itunes
                )
    pipeline = [s for s in FSM if s in kwargs.keys() and kwargs[s] is True]
    if len(pipeline) == 0:
        pipeline = FSM
    for step in pipeline:
        sys.stderr.write("INFO: Running step: {}".format(step))
        runs[step](**kwargs)
