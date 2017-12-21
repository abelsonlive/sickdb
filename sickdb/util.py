import os
import re
import subprocess

re_space = re.compile("\s+")


def path_here(f, *args):
    """
    Get the current directory and absolute path of a file.
    """
    return os.path.abspath(os.path.join(os.path.dirname(f), *args))


def path_get_ext(path):
    """
    get a filepath's extension.
    """
    _, ext = os.path.splitext(path)
    if not ext:
        return None
    if ext.startswith('.'):
        ext = ext[1:]
    return ext.lower()


def path_list(p):
    """
    Recursively list files under a directory.
    """
    return (os.path.join(dp, f) for dp, dn, fn in
            os.walk(os.path.expanduser(p)) for f in fn)


def listify(v):
    if not isinstance(v, list):
        v = [v]
    return v


def unlistify(v):
    if isinstance(v, list):
        if not len(v):
            v = None
        else:
            v = v[0]
    return v


def std_string(s):
    if not s:
        return ""
    return re_space.sub(" ", s.replace('"', "'").replace('`', "'").replace('/', ' ')).strip()


def sys_exec(cmd):
    """
    Run a shell command.
    """
    class _proc(object):

        def __init__(self, command):
            self.command = command
            self._stdin = None
            self._stdout = None
            self._stdout_text = None
            self._stderr_text = None
            self._returncode = None

        def set_stdin(self, stdin):
            self._stdin = stdin

        def set_stdout(self, stdout):
            self._stdout = stdout

        def set_stderr(self, stderr):
            self._stderr = stderr

        @property
        def stdin(self):
            return 'stdin'

        @property
        def stdout(self):
            if self._stdout_text is not None:
                return self._stdout_text

        @property
        def stderr(self):
            if self._stderr_text is not None:
                return self._stderr_text

        @property
        def returncode(self):
            if self._returncode is not None:
                return self._returncode

        @property
        def ok(self):
            if self._returncode is not None:
                return self.returncode is 0

        @property
        def subprocess(self):
            if self._subprocess is not None:
                return self._subprocess

        def start(self):
            self._subprocess = subprocess.Popen(
                args=self.command,
                shell=True,
                stdin=self._stdin if self._stdin else subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

        def wait(self, unread=False):
            self._returncode = self._subprocess.wait()
            if self._subprocess.stdout is not None and not unread:
                self._stdout_text = self._subprocess.stdout.read().decode()

        def run(self):
            self.start()
            self.wait()

        def __repr__(self):
            return '<Process: {0}>'.format(self.command)

    p = _proc(cmd)
    p.run()
    return p
