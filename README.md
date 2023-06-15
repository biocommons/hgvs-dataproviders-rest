# biocommons.uta-rest Test Package

This repo provides a template for biocommons Python packages.  Here's how to use it:

1. Click the [Use this template](https://github.com/biocommons/uta-rest/generate)
   button. Name the new repo like "biocommons.something".
1. Clone your repo locally.
1. In the repo, type `make rename`. The new name will be chosen based on the repo name.
1. Remove this header.
1. Commit and push.

## Installation

To install from pypi: ```pip install biocommons.uta-rest```

## Developer Setup

Setup like this:

    make devready
    source venv/bin/activate

Code reformatting:

    make reformat

Test:

    make test   # for current environment
    make tox    # for Python 3.9 and Python 3.10

Build:

    git tag 0.0.0
    make build

Try it:

    $ python3 -m biocommons.uta-rest
    Marvin says:
    There's only one life-form as intelligent as me within thirty parsecs...
           
    $ marvin-quote 
    Marvin says:
    You think you've got problems? What are you supposed to do if you...
    
    $ ipython
    >>> from biocommons.uta-rest import __version__, get_quote_from_marvin
    >>> __version__
    '0.1.dev8+gd5519a8.d20211123'
    >>> get_quote()
    "The first ten million years were the worst, ...


# Features

## Code structure and features

* Modern pyproject.toml with setuptools
* Versioning based on git tag (only)
* Easy development setup
* Support for namespaces
* Testing with coverage using pytest; tests may be in `tests/`, embedded in the package, and in doc strings
* Examples for logging and package data
* Command-line with argument parsing with argparse

## DevOps

* Quality tools: Code reformatting with black and isort
* GitHub Actions for testing and packaging

# To Do

* Docs (mkdocs w/mkdocstrings or sphinx)
* Dockerfile
* test only certain tags
* fixture example
