# brlib

[![Tests](https://github.com/john-bieren/brlib/actions/workflows/test.yml/badge.svg)](https://github.com/john-bieren/brlib/actions/workflows/test.yml)
[![PyPI Latest Release](https://img.shields.io/pypi/v/brlib?label=PyPI&logo=pypi&logoColor=ffe873&color=0073b7)](https://pypi.org/project/brlib)
[![Python Versions](https://img.shields.io/pypi/pyversions/brlib?label=Python%20Versions)](https://pypi.org/project/brlib)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)

A library for collecting baseball statistics from
[Baseball Reference](https://www.baseball-reference.com).

> [!IMPORTANT]
> brlib is in beta, breaking changes are possible until the release of version 1.

## Key Features

* `Game`, `Player`, and `Team` classes give you easy access to all associated data in one place,
  with attributes for stats tables, information, and more.
* Aggregate these into `GameSet`, `PlayerSet`, or `TeamSet` classes, which have similar attributes,
  for easy analysis of larger samples.
* Quickly search for games, players, and teams of interest, and gather their stats without violating
  the [rate limit](https://www.sports-reference.com/429.html).

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

## Data Use

Since brlib gathers data from Baseball Reference, your use of this data is subject to their
[data use policy](https://www.sports-reference.com/data_use.html).
