import os
import argparse
import yaml
import datetime

import dateutil.parser
import pytz
from blessings import Terminal
from operator import attrgetter
from babel.dates import format_timedelta

from codereview import util

TERM = Terminal()
ARG_DEFAULTS = {
    'strategy': ('merge', 'rebase'),
    'branch': 'meta/review',
    'scoring': 2,
}


class Runner(object):
    def __init__(self, ns):
        self.ns = ns
        self.reviews = []
        self.config = {}

    def setup(self):
        self.settings = os.path.join(util.GIT_ROOT, '.codereview.yaml')
        self.has_settings = os.path.isfile(self.settings)

        if self.has_settings:
            with open(self.settings) as f:
                self.__dict__.update(yaml.load(f))

    def list(self):
        for x, review in enumerate(self.reviews, start=1):
            review.print_short(x)

    def show(self, index):
        self.reviews[index - 1].show(index)

    def init(self):
        """
        Create the code review settings file and the special branch

        """

        if self.has_settings:
            print(
                TERM.bold_red('Error:'),
                'Settings file already exists. Doing nothing.'
            )
            return

        new_settings = {
            'strategy': self.ns.strategy,
            'branch': self.ns.branch,
            'scoring': self.ns.scoring,
        }

        with open(self.settings, 'w') as f:
            f.write(yaml.dump(new_settings, default_flow_style=False))

        print(
            TERM.bold_green('Yay!'),
            'Wrote settings file {0}'.format(self.settings)
        )

    def load_reviews(self):
        files = util.git('ls-tree', '-r', self.branch, '--name-only')

        for f in files.strip().split('\n'):
            if not f:
                continue

            content = util.git('show', '{0}:{1}'.format(self.branch, f))
            review = Review.load(content)
            self.reviews.append(review)

        self.reviews = sorted(
            self.reviews,
            key=attrgetter('open'),
            reverse=True
        )


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

    def merge(self):
        pass

    @staticmethod
    def load(content):
        review = Review(yaml.load(content))
        review.setup()
        return review

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

        data.append('Added by ' + Reviewer.get(self.by).nice())

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
                Reviewer.get(email).nice() +
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


class Reviewer(object):
    authors = {}

    def __init__(self, email, name):
        self.email = email
        self.name = name

    @staticmethod
    def get(email):
        if not Reviewer.authors:
            # Fill the authors cache
            Reviewer.authors = Reviewer.load_authors()

        name = Reviewer.authors.get(email)
        return Reviewer(email, name)

    @staticmethod
    def load_authors():
        """
        Use git log to find all contributors in the repo.

        """

        ret = {}
        for token in util.git('log', '--format=%aE:::%aN').split('\n'):
            email, name = token.split(':::')
            ret[email] = name
        return ret

    def nice(self):
        # Use the name if it's available, otherwise just use the email.
        return TERM.bold_cyan(self.name if self.name else self.email)


def setup_arguments():
    parser = argparse.ArgumentParser('codereview')
    subparsers = parser.add_subparsers(help="Core commands", dest="command")

    init = subparsers.add_parser(
        'init',
        help="Start using code review for this repository"
    )
    init.add_argument(
        '--branch',
        help="Target meta branch to use",
        default=ARG_DEFAULTS['branch'],
        metavar='<branchname>',
    )
    init.add_argument(
        '--scoring',
        help="Scoring scale to use",
        default=ARG_DEFAULTS['scoring'],
        type=int,
        metavar='<score>',
    )
    init.add_argument(
        '--strategy',
        help="Merge strategy to use",
        default='merge',
        choices=ARG_DEFAULTS['strategy'],
    )

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

    runner = Runner(ns)
    runner.setup()

    if not ns.command or ns.command == 'list':
        runner.load_reviews()
        runner.list()

    if ns.command == 'init':
        runner.init()

    if ns.command == 'show':
        runner.load_reviews()
        runner.show(ns.id)

    if ns.command == 'new':
        print('Creating new review')


if __name__ == "__main__":
    main()
