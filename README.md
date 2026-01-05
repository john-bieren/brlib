# brlib

![Tests](https://github.com/john-bieren/brlib/actions/workflows/test.yml/badge.svg)
[![PyPI Latest Release](https://img.shields.io/pypi/v/brlib.svg)](https://pypi.org/project/brlib)

A Python library for collecting baseball statistics from [Baseball Reference](https://www.baseball-reference.com).

> [!IMPORTANT]
> brlib is in beta, breaking changes are possible until the release of version 1.

## Key Features

* `Game`, `Player`, and `Team` classes give you easy access to all associated data in one place, with attributes for stats tables, information, and more.
* Aggregate these into `Games`, `Players`, or `Teams` classes, which contain similar attributes, for easy analysis of larger samples.
* Quickly search for games, players, and teams of interest, and gather their stats without violating the [rate limit](https://www.sports-reference.com/bot-traffic.html).

Learn more by reading the documentation on the [wiki](https://github.com/john-bieren/brlib/wiki).

## Install

brlib can be installed using pip:

```
pip install brlib
```

or from this repo, in which case you'll want to install the development dependencies as well:

```
git clone https://github.com/john-bieren/brlib.git
cd brlib
pip install -e .[dev]
```

Once installed, you can import brlib into your Python scripts:

```python
import brlib as br
```
