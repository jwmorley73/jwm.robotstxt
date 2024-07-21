[![build status](https://github.com/jwmorley73/jwm.robotstxt/actions/workflows/release.yaml/badge.svg)](https://github.com/jwmorley73/jwm.robotstxt/actions/workflows/release.yaml)

# jwm.robotstxt

## Python Wrapper for Googles Robotstxt Parser

Provides python access to Googles parser for `robot.txt` files as used by their `GoogleBot` webscraper. 

Websites may provide an optional `robots.txt` file in their domains root to govern the access and behavior of web scrapers. One of the most famous webscrapers `GoogleBot` is responsible for promoting this standard and sites interested in SEO will closely conform to `GoogleBot` behavior.

All credit for the parser goes to the Google team who created,  open sourced and promoted it.

> SEO (Search Engine Optimization): The process of modifying a websites content or metadata to boost rankings in search engines page indexes. Higher rankings lead to higher positions in user searches leading to more visitors. For further details, see the [SEO wikipedia page](https://en.wikipedia.org/wiki/Search_engine_optimization).

## Usage

Basic usage using the `RobotsMatcher` class provided by Google.
```python
import jwm.robotstxt.googlebot

robotstxt = """
user-agent: GoodBot
allowed: /path
"""

matcher = jwm.robotstxt.googlebot.RobotsMatcher()
assert matcher.AllowedByRobots(robotstxt, ("GoodBot",), "/path")
```

Check out the [documentation](https://jwmorley73.github.io/jwm.robotstxt/) for further details. For more use cases, see the test cases for [jwm.robotstxt](/tests/jwm/robotstxt/test_googlebot.py) and [robotstxt](https://github.com/google/robotstxt/blob/a732377373e8bbee9f720b52020e2a8d5dd19cf8/robots_test.cc).

## Installation

Install from Pypi under the `jwm.robotstxt` distribution.

```shell
pip install jwm.robotstxt
```

Import into your program through the `jwm.robotstxt.googlebot` package.

```python
import jwm.robotstxt.googlebot
```

### Virtual Environment

It is highly recommended to install python projects into a virtual environment, see [PEP405](https://peps.python.org/pep-0405/) for motivations.

Create a virtual environment in the `.venv` directory.

```shell
python3 -m venv ./.venv
```

Activate with the correct command for your system.
```shell
# Linux/MacOS
. ./.venv/bin/activate
```

```shell
# Windows
.\.venv\Scripts\activate
```

### Installing from source

Make sure you have cloned the repository **and** its submodules.

```shell
git clone --recurse-submodules https://github.com/jwmorley73/jwm.robotstxt.git
```

Install the project using pip. This will build the required `robotstxt` static library files and link them into the produced python package. 

```shell
pip install .
```

If you want to include the developer tooling, add the `dev` optional dependencies.

```shell
pip install .[dev]
```

## Known Issues

 - Windows 32 bit is not supported.
