"""Tests for bindings between python and C++.

We can rely on the C++ robotstxt testing library for greater testing depth. We
only need to focus on the bindings being functional python side rather than
looking at specific behaviours.
"""

import typing

import pytest

import jwm.robotstxt.googlebot

robotstxt = """
user-agent: *
allowed: /path
disallow: /other

user-agent: GoodBot
allowed: /path

user-agent: BadBot
disallow: /path
"""


@pytest.fixture
def robots_matcher() -> jwm.robotstxt.googlebot.RobotsMatcher:
    return jwm.robotstxt.googlebot.RobotsMatcher()


@pytest.mark.parametrize(
    ("user_agent", "valid"), (("GoodBot", True), ("Bad%Bot", False))
)
def test_RobotsMatcher_IsValidUserAgentToObey(user_agent: str, valid: bool) -> None:
    assert (
        jwm.robotstxt.googlebot.RobotsMatcher.IsValidUserAgentToObey(user_agent)
        == valid
    )


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "url", "allowed"),
    (
        (robotstxt, ("GoodBot", "BadBot"), "www.example.com/path", True),
        (robotstxt, ("BadBot", "TerribleBot"), "www.example.com/path", False),
    ),
)
def test_RobotsMatcher_AllowedByRobots(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    url: str,
    allowed: bool,
) -> None:
    assert robots_matcher.AllowedByRobots(robotstxt, user_agents, url) == allowed


@pytest.mark.parametrize(
    ("robotstxt", "user_agent", "url", "allowed"),
    (
        (robotstxt, "GoodBot", "www.example.com/path", True),
        (robotstxt, "BadBot", "www.example.com/path", False),
    ),
)
def test_RobotsMatcher_OneAgentAllowedByRobots(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
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
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    user_agents: typing.Sequence[str],
    path: str,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "disallowed"),
    (
        (
            robotstxt,
            ("GoodBot",),
            "/path",
            False,
        ),
        (
            robotstxt,
            ("BadBot",),
            "/path",
            True,
        ),
        (
            robotstxt,
            ("AnotherBot",),
            "/other",
            True,
        ),
    ),
)
def test_RobotsMatcher_disallow(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    disallowed: bool,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    jwm.robotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.disallow() == disallowed


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "disallowed"),
    (
        (
            robotstxt,
            ("GoodBot",),
            "/path",
            False,
        ),
        (
            robotstxt,
            ("BadBot",),
            "/path",
            True,
        ),
        (
            robotstxt,
            ("AnotherBot",),
            "/other",
            False,
        ),
    ),
)
def test_RobotsMatcher_disallow_ignore_global(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    disallowed: bool,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    jwm.robotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.disallow_ignore_global() == disallowed


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "disallowed"),
    (
        (
            robotstxt,
            ("GoodBot",),
            "/",
            True,
        ),
        (
            robotstxt,
            ("BadBot",),
            "/",
            True,
        ),
        (
            robotstxt,
            ("AnotherBot",),
            "/",
            False,
        ),
    ),
)
def test_RobotsMatcher_ever_seen_specific_agent(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    disallowed: bool,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    jwm.robotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.ever_seen_specific_agent() == disallowed


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "line"),
    (
        (
            robotstxt,
            ("GoodBot",),
            "/path",
            7,
        ),
        (
            robotstxt,
            ("BadBot",),
            "/path",
            10,
        ),
        (
            robotstxt,
            ("AnotherBot",),
            "/path",
            3,
        ),
    ),
)
def test_RobotsMatcher_matching_line(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    line: int,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    jwm.robotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.matching_line() == line


@pytest.mark.parametrize(
    ("string", "user_agent"),
    (
        ("GoodBot", "GoodBot"),
        ("GoodBot/2", "GoodBot"),
    ),
)
def test_RobotsMatcher_ExtractUserAgent(
    string: str,
    user_agent: str,
) -> None:
    assert jwm.robotstxt.googlebot.RobotsMatcher.ExtractUserAgent(string) == user_agent


@pytest.mark.parametrize(
    ("robotstxt", "user_agents", "path", "seen"),
    (
        (robotstxt, ("GoodBot", "BadBot"), "/path", True),
        (
            robotstxt,
            ("AnotherBot",),
            "/path",
            False,
        ),
    ),
)
def test_RobotsMatcher_seen_any_agent(
    robots_matcher: jwm.robotstxt.googlebot.RobotsMatcher,
    robotstxt: str,
    user_agents: typing.Sequence[str],
    path: str,
    seen: bool,
) -> None:
    robots_matcher.InitUserAgentsAndPath(user_agents, path)
    jwm.robotstxt.googlebot.ParseRobotsTxt(robotstxt, robots_matcher)
    assert robots_matcher.seen_any_agent() == seen
