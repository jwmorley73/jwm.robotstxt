"""Tests for bindings between python and C++.

We can rely on the C++ robotstxt testing library for greater testing depth. We
only need to focus on the bindings being functional python side rather than
looking at specific behaviours.
"""

import typing

import pytest

import pyrobotstxt.googlebot

robotstxt = """
user-agent: GoodBot
allowed: /path

user-agent: BadBot
disallow: /path
"""


@pytest.fixture
def robots_matcher() -> pyrobotstxt.googlebot.RobotsMatcher:
    return pyrobotstxt.googlebot.RobotsMatcher()


@pytest.mark.parametrize(
    ("user_agent", "valid"), (("GoodBot", True), ("Bad%Bot", False))
)
def test_RobotsMatcher_IsValidUserAgentToObey(user_agent: str, valid: bool) -> None:
    assert (
        pyrobotstxt.googlebot.RobotsMatcher.IsValidUserAgentToObey(user_agent) == valid
    )


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "url", "allowed"),
    (
        (robotstxt, ("GoodBot", "BadBot"), "www.example.com/path", True),
        (robotstxt, ("BadBot", "TerribleBot"), "www.example.com/path", False),
    ),
)
def test_RobotsMatcher_AllowedByRobots(
    robots_matcher: pyrobotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    url: str,
    allowed: bool,
) -> None:
    user_agents = pyrobotstxt.googlebot.VectorString(user_agents)
    assert robots_matcher.AllowedByRobots(robotstxt, user_agents, url) == allowed


@pytest.mark.parametrize(
    ("robotstxt", "user_agent", "url", "allowed"),
    (
        (robotstxt, "GoodBot", "www.example.com/path", True),
        (robotstxt, "BadBot", "www.example.com/path", False),
    ),
)
def test_RobotsMatcher_OneAgentAllowedByRobots(
    robots_matcher: pyrobotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agent: str,
    url: str,
    allowed: bool,
) -> None:
    assert robots_matcher.OneAgentAllowedByRobots(robotstxt, user_agent, url) == allowed


@pytest.mark.parametrize(
    ("user_agents", "path"),
    (
        (("GoodBot",), "/"),
        (("GoodBot", "BadBot"), "/path?query"),
    ),
)
def test_RobotsMatcher_InitUserAgentsAndPath(
    robots_matcher: pyrobotstxt.googlebot.RobotsMatcher,
    user_agents: typing.Sequence[str],
    path: str,
) -> None:
    user_agents = pyrobotstxt.googlebot.VectorString(user_agents)
    robots_matcher.InitUserAgentsAndPath(user_agents, path)

@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "disallowed"),
    (
        (robotstxt, ["GoodBot",], "/path", False),
        (robotstxt, ["BadBot",], "/path", False),
    )
)
def test_RobotsMatcher_disallow(
    robots_matcher: pyrobotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    disallowed: str
) -> None:
    user_agents = pyrobotstxt.googlebot.VectorString(user_agents)
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    pyrobotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.disallow() == disallowed
