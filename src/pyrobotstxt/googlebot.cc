#include <pybind11/pybind11.h>

#include "robots.h"
#include "absl/strings/string_view.h"


namespace py = pybind11;
namespace gb = googlebot;


namespace PYBIND11_NAMESPACE { namespace detail {
// https://github.com/pybind/pybind11_abseil/blob/2c49cb53c14735728b4d0c45721e5cac65b0d5a0/pybind11_abseil/absl_casters.h#L600
  #ifndef ABSL_USES_STD_STRING_VIEW
  template <>
      struct type_caster<absl::string_view>
          :string_caster<absl::string_view, true>
      {};
  #endif
}}

class PyRobotsParseHandler : public gb::RobotsParseHandler {
public:
  using gb::RobotsParseHandler::RobotsParseHandler;

  void HandleRobotsStart() override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleRobotsStart);
  };

  void HandleRobotsEnd() override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleRobotsEnd);
  };

  void HandleUserAgent(int line_num, absl::string_view value) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleUserAgent,
                          line_num, value);
  }

  void HandleAllow(int line_num, absl::string_view value) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleAllow, line_num,
                          value);
  }

  void HandleDisallow(int line_num, absl::string_view value) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleDisallow,
                          line_num, value);
  };

  void HandleSitemap(int line_num, absl::string_view value) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleSitemap,
                          line_num, value);
  };

  void HandleUnknownAction(int line_num, absl::string_view action,
                          absl::string_view value) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleUnknownAction,
                          line_num, action, value);
  };

  void ReportLineMetadata(int line_num,
                          const gb::RobotsParseHandler::LineMetadata& metadata
                          ) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, ReportLineMetadata,
                          line_num, metadata);
  };
};

PYBIND11_MODULE(googlebot, m) {
  py::options options;
  options.disable_function_signatures();

  m.doc() = R"(
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
  )";

  py::class_<gb::RobotsParseHandler, PyRobotsParseHandler> robotsParseHandler(
      m, "RobotsParseHandler", py::dynamic_attr());

  robotsParseHandler.doc() = R"(
Handler for directives found in robots.txt. These callbacks are called by
ParseRobotsTxt() in the sequence they have been found in the file.
  )";

  robotsParseHandler.def(py::init<>(),
                         R"(
__init__(self: pyrobotstxt.googlebot.RobotsParseHandler, /) -> None
                         )")
    .def("HandleRobotsStart",
         &gb::RobotsParseHandler::HandleRobotsStart,
         R"(
HandleRobotsStart(self: pyrobotstxt.googlebot.RobotsParseHandler, /) -> None
         )")
    .def("HandleRobotsEnd",
         &gb::RobotsParseHandler::HandleRobotsEnd,
         R"(
HandleRobotsEnd(self: pyrobotstxt.googlebot.RobotsParseHandler, /) -> None
         )")
    .def("HandleUserAgent",
         &gb::RobotsParseHandler::HandleUserAgent,
         R"(
HandleUserAgent(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, value: str, /) -> None
         )")
    .def("HandleAllow",
         &gb::RobotsParseHandler::HandleAllow,
         R"(
HandleAllow(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, value: str, /) -> None
         )")
    .def("HandleDisallow",
         &gb::RobotsParseHandler::HandleDisallow,
         R"(
HandleDisallow(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, value: str, /) -> None
         )")
    .def("HandleSitemap",
         &gb::RobotsParseHandler::HandleSitemap,
         R"(
HandleSitemap(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, value: str, /) -> None
         )")
    .def("HandleUnknownAction",
         &gb::RobotsParseHandler::HandleUnknownAction,
         R"(
HandleUnknownAction(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, action: str, value: str, /) -> None

Any other unrecognized name/value pairs.
         )");
  
  py::class_<gb::RobotsParseHandler::LineMetadata>(
    robotsParseHandler,
    "LineMetaData",
    py::dynamic_attr())
      .def_readwrite("is_empty",
                    &gb::RobotsParseHandler::LineMetadata::is_empty,
                    R"(
Indicates if the line is totally empty.
                    )")
      .def_readwrite("has_comment",
                    &gb::RobotsParseHandler::LineMetadata::has_comment,
                    R"(
Indicates if the line has a comment (may have content before it).
                    )")
      .def_readwrite("is_comment",
                    &gb::RobotsParseHandler::LineMetadata::is_comment,
                    R"(
Indicates if the whole line is a comment.
                    )")
      .def_readwrite("has_directive",
                    &gb::RobotsParseHandler::LineMetadata::has_directive,
                    R"(
Indicates that the line has a valid robots.txt directive and one of the
`Handle*` methods will be called.
                    )")
      .def_readwrite("is_acceptable_typo",
          &gb::RobotsParseHandler::LineMetadata::is_acceptable_typo,
          R"(
Indicates that the found directive is one of the acceptable typo variants
of the directive. See the key functions in ParsedRobotsKey for accepted
typos.
          )")
      .def_readwrite("is_line_too_long",
                    &gb::RobotsParseHandler::LineMetadata::is_line_too_long,
                    R"(
Indicates that the line is too long, specifically over 2083 * 8 bytes.
                    )")
      .def_readwrite("is_missing_colon_separator",
          &gb::RobotsParseHandler::LineMetadata::is_missing_colon_separator,
          R"(
Indicates that the key-value pair is missing the colon separator.
          )");

  robotsParseHandler
    .def("ReportLineMetadata",
         &gb::RobotsParseHandler::ReportLineMetadata,
         R"(
ReportLineMetadata(self: pyrobotstxt.googlebot.RobotsParseHandler, line_num: int, metadata: pyrobotstxt.googlebot.RobotsParseHandler.LineMetadata, /) -> None
         )");

  m.def("ParseRobotsTxt",
        &gb::ParseRobotsTxt,
        R"(
ParseRobotsTxt(robots_body: str, parse_callback: pyrobotstxt.googlebot.RobotsParseHandler, /) -> None

Parses body of a robots.txt and emits parse callbacks. This will accept
typical typos found in robots.txt, such as 'disalow'.

Note, this function will accept all kind of input but will skip
everything that does not look like a robots directive.
        )");
  
  py::class_<gb::RobotsMatcher> robotsMatcher(m,
                                              "RobotsMatcher",
                                              py::dynamic_attr());

  robotsMatcher.doc() = R"(
RobotsMatcher - matches robots.txt against URLs.

The Matcher uses a default match strategy for Allow/Disallow patterns which
is the official way of Google crawler to match robots.txt. It is also
possible to provide a custom match strategy.

The entry point for the user is to call one of the *AllowedByRobots()
methods that return directly if a URL is being allowed according to the
robots.txt and the crawl agent.
The RobotsMatcher can be re-used for URLs/robots.txt but is not thread-safe.
  )";

  robotsMatcher.def(
      py::init<>(),
      R"(
__init__(self: pyrobotstxt.googlebot.RobotsMatcher, /) -> None

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
      )")
    .def_static("IsValidUserAgentToObey",
                &gb::RobotsMatcher::IsValidUserAgentToObey,
                R"(
IsValidUserAgentToObey(user_agent: str, /) -> bool

Verifies that the given user agent is valid to be matched against
robots.txt. Valid user agent strings only contain the characters
[a-zA-Z_-].
                )")
    .def("AllowedByRobots",
         &gb::RobotsMatcher::AllowedByRobots,
         R"(
AllowedByRobots(self: pyrobotstxt.googlebot.RobotsMatcher, robots_body: str, user_agents: typing.Sequence[str], url: str, /) -> bool

Returns true iff 'url' is allowed to be fetched by any member of
the "user_agents" vector. 'url' must be %-encoded according to
RFC3986.
         )")
    .def("OneAgentAllowedByRobots",
         &gb::RobotsMatcher::OneAgentAllowedByRobots,
         R"(
OneAgentAllowedByRobots(self: pyrobotstxt.googlebot.RobotsMatcher, robots_txt: str, user_agent: str, url: str, /) -> bool

Do robots check for 'url' when there is only one user agent. 'url' must
be %-encoded according to RFC3986.
         )")
    .def("disallow",
         &gb::RobotsMatcher::disallow,
         R"(
disallow(self: pyrobotstxt.googlebot.RobotsMatcher, /) -> bool

Returns true if we are disallowed from crawling a matching URI.
         )")
    .def("disallow_ignore_global",
         &gb::RobotsMatcher::disallow_ignore_global,
         R"(
disallow_ignore_global(self: pyrobotstxt.googlebot.RobotsMatcher, /) -> bool

Returns true if we are disallowed from crawling a matching URI. Ignores any
rules specified for the default user agent, and bases its results only on
the specified user agents.
         )")
    .def("ever_seen_specific_agent",
         &gb::RobotsMatcher::ever_seen_specific_agent,
         R"(
ever_seen_specific_agent(self: pyrobotstxt.googlebot.RobotsMatcher, /) -> bool

Returns true iff, when AllowedByRobots() was called, the robots file
referred explicitly to one of the specified user agents.
         )")
    .def("matching_line",
         &gb::RobotsMatcher::matching_line,
         R"(
matching_line(self: pyrobotstxt.googlebot.RobotsMatcher, /) -> int

Returns the line that matched or 0 if none matched.
         )");
};