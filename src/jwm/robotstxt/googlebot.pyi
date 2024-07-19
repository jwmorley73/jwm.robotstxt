"""
This file implements the standard defined by the Robots Exclusion Protocol
(REP) internet draft (I-D).
  https://www.rfc-editor.org/rfc/rfc9309.html

Google doesn't follow the standard strictly, because there are a lot of
non-conforming robots.txt files out there, and we err on the side of
disallowing when this seems intended.

An more user-friendly description of how Google handles robots.txt can be
found at:
  https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt

This library provides a low-level parser for robots.txt (ParseRobotsTxt()),
and a matcher for URLs against a robots.txt (class RobotsMatcher).
"""

import abc
import dataclasses
import typing

class RobotsParseHandler(abc.ABC):
    """
    Handler for directives found in robots.txt. These callbacks are called by
    ParseRobotsTxt() in the sequence they have been found in the file.
    """

    @abc.abstractmethod
    def HandleRobotsStart(self, /) -> None: ...
    @abc.abstractmethod
    def HandleRobotsEnd(self, /) -> None: ...
    @abc.abstractmethod
    def HandleUserAgent(self, line_num: int, value: str, /) -> None: ...
    @abc.abstractmethod
    def HandleAllow(self, line_num: int, value: str, /) -> None: ...
    @abc.abstractmethod
    def HandleDisallow(self, line_num: int, value: str, /) -> None: ...
    @abc.abstractmethod
    def HandleSitemap(self, line_num: int, value: str, /) -> None: ...
    @abc.abstractmethod
    def HandleUnknownAction(self, line_num: int, action: str, value: str, /) -> None:
        """
        Any other unrecognized name/value pairs.
        """

    @dataclasses.dataclass
    class LineMetadata:

        is_empty: bool = False
        """
        Indicates if the line is totally empty.
        """

        has_comment: bool = False
        """
        Indicates if the line has a comment (may have content before it).
        """

        is_comment: bool = False
        """
        Indicates if the whole line is a comment.
        """

        has_directive: bool = False
        """
        Indicates that the line has a valid robots.txt directive and one of the
        `Handle*` methods will be called.
        """

        is_acceptable_typo: bool = False
        """
        Indicates that the found directive is one of the acceptable typo variants
        of the directive. See the key functions in ParsedRobotsKey for accepted
        typos.
        """

        is_line_too_long: bool = False
        """
        Indicates that the line is too long, specifically over 2083 * 8 bytes.
        """

        is_missing_colon_separator: bool = False
        """
        Indicates that the key-value pair is missing the colon separator.
        """

    @abc.abstractmethod
    def ReportLineMetadata(
        self, line_num: str, metadata: RobotsParseHandler.LineMetadata, /
    ) -> None: ...

def ParseRobotsTxt(robots_body: str, parse_callback: RobotsParseHandler, /) -> None:
    """
    Parses body of a robots.txt and emits parse callbacks. This will accept
    typical typos found in robots.txt, such as 'disalow'.

    Note, this function will accept all kind of input but will skip
    everything that does not look like a robots directive.)

    Wrapper Note (jwm.robotstxt): If using with RobotsMatcher make sure to call the
    InitUserAgentsAndPath first to initialise the internal user agents and path
    properties.
    """

class RobotsMatcher(RobotsParseHandler):
    """
    RobotsMatcher - matches robots.txt against URLs.

    The Matcher uses a default match strategy for Allow/Disallow patterns which
    is the official way of Google crawler to match robots.txt. It is also
    possible to provide a custom match strategy.

    The entry point for the user is to call one of the *AllowedByRobots()
    methods that return directly if a URL is being allowed according to the
    robots.txt and the crawl agent.
    The RobotsMatcher can be re-used for URLs/robots.txt but is not thread-safe.
    """

    def __init__(self, /) -> None:
        """
        Create a RobotsMatcher with the default matching strategy. The default
        matching strategy is longest-match as opposed to the former internet draft
        that provisioned first-match strategy. Analysis shows that longest-match,
        while more restrictive for crawlers, is what webmasters assume when writing
        directives. For example, in case of conflicting matches (both Allow and
        Disallow), the longest match is the one the user wants. For example, in
        case of a robots.txt file that has the following rules
          Allow: /
          Disallow: /cgi-bin
        it's pretty obvious what the webmaster wants: they want to allow crawl of
        every URI except /cgi-bin. However, according to the expired internet
        standard, crawlers should be allowed to crawl everything with such a rule.
        """

    @staticmethod
    def IsValidUserAgentToObey(user_agent: str, /) -> bool:
        """
        Verifies that the given user agent is valid to be matched against
        robots.txt. Valid user agent strings only contain the characters
        [a-zA-Z_-].
        """

    def AllowedByRobots(
        self, robots_body: str, user_agents: typing.Sequence[str], url: str, /
    ) -> bool:
        """
        Returns true iff 'url' is allowed to be fetched by any member of
        the "user_agents" vector. 'url' must be %-encoded according to
        RFC3986.
        """

    def OneAgentAllowedByRobots(
        self, robots_txt: str, user_agent: str, url: str, /
    ) -> bool:
        """
        Do robots check for 'url' when there is only one user agent. 'url' must
        be %-encoded according to RFC3986.
        """

    def disallow(self, /) -> bool:
        """
        Returns true if we are disallowed from crawling a matching URI.
        """

    def disallow_ignore_global(self, /) -> bool:
        """
        Returns true if we are disallowed from crawling a matching URI. Ignores any
        rules specified for the default user agent, and bases its results only on
        the specified user agents.
        """

    def ever_seen_specific_agent(self, /) -> bool:
        """
        Returns true iff, when AllowedByRobots() was called, the robots file
        referred explicitly to one of the specified user agents.
        """

    def matching_line(self, /) -> int:
        """
        Returns the line that matched or 0 if none matched.
        """

    @staticmethod
    def ExtractUserAgent(user_agent: str) -> str:
        """
        Extract the matchable part of a user agent string, essentially stopping at
        the first invalid character.
        Example: 'Googlebot/2.1' becomes 'Googlebot'
        """

    def InitUserAgentsAndPath(
        self, user_agents: typing.Sequence[str], path: str
    ) -> None:
        """
        Initialize next path and user-agents to check. Path must contain only the
        path, params, and query (if any) of the url and must start with a '/'.
        """

    def seen_any_agent(self) -> bool:
        """
        Returns true if any user-agent was seen.
        """
