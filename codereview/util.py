import os
import sys
import subprocess as sp


def get_git_root():
    if os.path.isdir('.git'):
        return os.getcwd()

    proc = sp.Popen(
        ['git', 'rev-parse', '--git-dir'],
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )
    stdout, stderr = [x.decode() for x in proc.communicate()]

    if stderr:
        print(stderr)
        sys.exit(128)

    if stdout == '.git\n':
        return os.getcwd()
    return os.path.dirname(stdout.strip())


GIT_ROOT = get_git_root()


def git(*args):
    # print('git: {0}'.format(' '.join(args)))
    proc = sp.Popen(
        ['git', '--git-dir={0}/.git'.format(GIT_ROOT)] + list(args),
        stdout=sp.PIPE,
        stderr=sp.PIPE,
    )
    stdout, stderr = [x.decode() for x in proc.communicate()]
    return stdout.strip()
