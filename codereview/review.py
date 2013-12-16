import sys
import os
import subprocess as sp
import argparse
import yaml
import datetime

import dateutil.parser
import pytz
from blessings import Terminal
from operator import attrgetter
from babel.dates import format_timedelta

TERM = Terminal()


class Runner(object):
    def __init__(self):
        self.reviews = []
        self.config = {}

    def setup(self):
        self.gitroot = self.get_git_root()

        with open(os.path.join(self.gitroot, '.codereview.yaml')) as f:
            self.__dict__.update(yaml.load(f))

    def list(self):
        for x, review in enumerate(self.reviews, start=1):
            review.print_short(x)

    def show(self, index):
        self.reviews[index - 1].show(index)

    def get_git_root(self):
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

    def load_reviews(self):
        files = self.git('ls-tree', '-r', self.branch, '--name-only')

        for f in files.strip().split('\n'):
            if not f:
                continue

            content = self.git('show', '{0}:{1}'.format(self.branch, f))
            review = Review.load(content)
            self.reviews.append(review)

        self.reviews = sorted(
            self.reviews,
            key=attrgetter('open'),
            reverse=True
        )

    def git(self, *args):
        # print('git: {0}'.format(' '.join(args)))
        proc = sp.Popen(
            ['git', '--git-dir={0}/.git'.format(self.gitroot)] + list(args),
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        stdout, stderr = [x.decode() for x in proc.communicate()]
        return stdout


class Review(object):
    def __init__(self, data):
        self.data = data
        self.created = None

    def setup(self):
        self.__dict__.update(self.data)
        self.created = dateutil.parser.parse(self.data['dates']['created'])
        self.abandoned = self.__dict__.get('abandoned', False)
        self.open = not (self.merged or self.abandoned)

    def new(self, branch, target):
        pass

    @staticmethod
    def load(content):
        review = Review(yaml.load(content))
        review.setup()
        return review

    def merge(self):
        pass

    def print_short(self, index):
        data = [
            TERM.bold_black('{0}) '.format(index)),
            TERM.bold_yellow(self.data['title']),
        ]

        data.append(
            TERM.bright_black(' (') +
            TERM.bold_blue(self.data['from']['branch']) +
            TERM.bright_black(':') +
            TERM.bold_cyan(self.data['onto'])
        )

        if self.merged:
            data.append(
                TERM.bright_black(', ') +
                TERM.bold_green('MERGED')
            )
        elif self.abandoned:
            data.append(
                TERM.bright_black(', ') +
                TERM.bold_red('ABANDONED')
            )

        data.append(TERM.bright_black(')'))

        print(''.join(data))

    def show(self, index):
        self.print_short(index)
        data = []

        data.append('Added by {0}'.format(TERM.bold_cyan(self.by)))

        relative = format_timedelta(
            datetime.datetime.now(pytz.utc) - self.created
        )
        data.append(TERM.bold_magenta(' {0} ago'.format(relative)))

        data.append('\n\n')
        data.append(self.body.strip())
        data.append('\n\n')

        scores = []
        for email, score in self.reviewers.items():
            scores.append(
                TERM.bold_cyan(email) +
                TERM.bright_black(': ')
            )
            if score >= 1:
                fun = TERM.bold_green
                score = '+{0}'.format(score)
            elif score == 0:
                fun = TERM.bold_white
            else:
                fun = TERM.bold_red

            scores.append(fun(str(score)))
            scores.append('\n')

        data.append(''.join(scores))

        print(''.join(data))


def setup_arguments():
    parser = argparse.ArgumentParser('codereview')
    subparsers = parser.add_subparsers(help="Core commands", dest="command")

    subparsers.add_parser(
        'new',
        help="Create a new review"
    )

    subparsers.add_parser(
        'list',
        help="List reviews"
    )

    show = subparsers.add_parser(
        'show',
        help="Detailed view of a review"
    )
    show.add_argument(
        'id', help="Review ID", default=1, nargs="?", type=int
    )

    return parser


def main():
    args = setup_arguments()
    ns = args.parse_args()

    runner = Runner()
    runner.setup()

    if not ns.command or ns.command == 'list':
        runner.load_reviews()
        runner.list()

    if ns.command == 'show':
        runner.load_reviews()
        runner.show(ns.id)

    if ns.command == 'new':
        print('Creating new review')


if __name__ == "__main__":
    main()
