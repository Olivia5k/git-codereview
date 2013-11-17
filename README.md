# git-eyeballs

**git-eyeballs** is a terminal based code review tool.  It stores review data in
special branches inside of the repository.

**git-eyeballs** is written using [RDD][rdd].  If this very paragraph is still
present when you read this, the RDD process is not yet complete and features
described in this README might not have been implemented yet.  There might be
dragons.

## Why?

* Other code review systems typically host a separate database with review
  data.  This means that all data about the state of the repository is not in
  the repository.  That's not how git is supposed to work.
* You can use whatever tools you are comfortable with for viewing diffs and
  working with the review.
* Also, you should never have to leave your terminal. &lt;3

## Features

* Locally stored reviews
* Comments and voting
* Merge control for completing the code reviews

## Installation

`python setup.py install`

Run `git eyeballs init` in a repository where you want to use it.

## Notes

The name?

*"Given enough eyeballs, all bugs are shallow."*

The current implementation interacts with git via the git binary.  This is
possibly suboptimal and a proper Python implementation should be considered.
However, as of this writing, none of them support Python 3, and that's
a dealbreaker.

## License

**git-eyeballs** is licensed under the MIT license.

[rdd]: http://tom.preston-werner.com/2010/08/23/readme-driven-development.html
