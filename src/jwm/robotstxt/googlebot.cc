#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

#include <string>
#include <vector>

#include "absl/strings/string_view.h"
#include "robots.h"

namespace py = pybind11;
namespace gb = googlebot;

namespace PYBIND11_NAMESPACE {
namespace detail {
// https://github.com/pybind/pybind11_abseil/blob/2c49cb53c14735728b4d0c45721e5cac65b0d5a0/pybind11_abseil/absl_casters.h#L600
#ifndef ABSL_USES_STD_STRING_VIEW
template <>
struct type_caster<absl::string_view> : string_caster<absl::string_view, true> {
};
#endif
}  // namespace detail
}  // namespace PYBIND11_NAMESPACE

class PyRobotsParseHandler : public gb::RobotsParseHandler {
 public:
  using gb::RobotsParseHandler::RobotsParseHandler;

  void HandleRobotsStart() override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleRobotsStart, );
  };

  void HandleRobotsEnd() override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, HandleRobotsEnd, );
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

  void ReportLineMetadata(
      int line_num,
      const gb::RobotsParseHandler::LineMetadata& metadata) override {
    PYBIND11_OVERRIDE_PURE(void, gb::RobotsParseHandler, ReportLineMetadata,
                           line_num, metadata);
  };
};

class PublicStatefulRobotsMatcher : public gb::RobotsMatcher {
 public:
  PublicStatefulRobotsMatcher() = default;
  ~PublicStatefulRobotsMatcher() = default;

  using gb::RobotsMatcher::ExtractUserAgent;
  using gb::RobotsMatcher::seen_any_agent;

  void InitUserAgentsAndPath(const std::vector<std::string>& user_agents,
                             const std::string& path) {
    this->user_agents = std::make_unique<std::vector<std::string>>(user_agents);
    this->path = std::make_unique<std::string>(path);
    return gb::RobotsMatcher::InitUserAgentsAndPath(this->user_agents.get(),
                                                    this->path->c_str());
  };

 private:
  std::unique_ptr<std::vector<std::string>> user_agents;
  std::unique_ptr<std::string> path;
};

PYBIND11_MODULE(googlebot, m) {
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

  robotsParseHandler.def(py::init<>())
      .def("HandleRobotsStart", &gb::RobotsParseHandler::HandleRobotsStart)
      .def("HandleRobotsEnd", &gb::RobotsParseHandler::HandleRobotsEnd)
      .def("HandleUserAgent", &gb::RobotsParseHandler::HandleUserAgent,
           py::arg("line_num"), py::arg("value"))
      .def("HandleAllow", &gb::RobotsParseHandler::HandleAllow,
           py::arg("line_num"), py::arg("value"))
      .def("HandleDisallow", &gb::RobotsParseHandler::HandleDisallow,
           py::arg("line_num"), py::arg("value"))
      .def("HandleSitemap", &gb::RobotsParseHandler::HandleSitemap,
           py::arg("line_num"), py::arg("value"))
      .def("HandleUnknownAction", &gb::RobotsParseHandler::HandleUnknownAction,
           py::arg("line_num"), py::arg("action"), py::arg("value"),
           R"(
Any other unrecognized name/value pairs.
         )");

  py::class_<gb::RobotsParseHandler::LineMetadata>(
      robotsParseHandler, "LineMetaData", py::dynamic_attr())
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
      .def_readwrite(
          "is_missing_colon_separator",
          &gb::RobotsParseHandler::LineMetadata::is_missing_colon_separator,
          R"(
Indicates that the key-value pair is missing the colon separator.
          )");

  robotsParseHandler.def("ReportLineMetadata",
                         &gb::RobotsParseHandler::ReportLineMetadata,
                         py::arg("line_num"), py::arg("metadata"));

  m.def("ParseRobotsTxt", &gb::ParseRobotsTxt, py::arg("robots_body"),
        py::arg("parse_callback").none(false),
        R"(
Parses body of a robots.txt and emits parse callbacks. This will accept
typical typos found in robots.txt, such as 'disalow'.

Note, this function will accept all kind of input but will skip
everything that does not look like a robots directive.

Wrapper Note (jwm.robotstxt): If using with RobotsMatcher make sure to call the
InitUserAgentsAndPath first to initialise the internal user agents and path
properties.
        )");

  py::class_<PublicStatefulRobotsMatcher> robotsMatcher(
      m, "RobotsMatcher", robotsParseHandler, py::dynamic_attr(),
      py::is_final());

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

  robotsMatcher
      .def(py::init<>(),
           R"(
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
                  &PublicStatefulRobotsMatcher::IsValidUserAgentToObey,
                  py::arg("user_agent"),
                  R"(
Verifies that the given user agent is valid to be matched against
robots.txt. Valid user agent strings only contain the characters
[a-zA-Z_-].
                )")
      .def("AllowedByRobots", &PublicStatefulRobotsMatcher::AllowedByRobots,
           py::arg("robots_body"), py::arg("user_agents").none(false),
           py::arg("url"),
           R"(
Returns true iff 'url' is allowed to be fetched by any member of
the "user_agents" vector. 'url' must be %-encoded according to
RFC3986.
         )")
      .def("OneAgentAllowedByRobots",
           &PublicStatefulRobotsMatcher::OneAgentAllowedByRobots,
           py::arg("robots_txt"), py::arg("user_agent"), py::arg("url"),
           R"(
Do robots check for 'url' when there is only one user agent. 'url' must
be %-encoded according to RFC3986.
         )")
      .def("disallow", &PublicStatefulRobotsMatcher::disallow,
           R"(
Returns true if we are disallowed from crawling a matching URI.
         )")
      .def("disallow_ignore_global",
           &PublicStatefulRobotsMatcher::disallow_ignore_global,
           R"(
Returns true if we are disallowed from crawling a matching URI. Ignores any
rules specified for the default user agent, and bases its results only on
the specified user agents.
         )")
      .def("ever_seen_specific_agent",
           &PublicStatefulRobotsMatcher::ever_seen_specific_agent,
           R"(
Returns true iff, when AllowedByRobots() was called, the robots file
referred explicitly to one of the specified user agents.
         )")
      .def("matching_line", &PublicStatefulRobotsMatcher::matching_line,
           R"(
Returns the line that matched or 0 if none matched.
         )")
      .def_static("ExtractUserAgent",
                  &PublicStatefulRobotsMatcher::ExtractUserAgent,
                  py::arg("user_agent"),
                  R"(
Extract the matchable part of a user agent string, essentially stopping at
the first invalid character.
Example: 'Googlebot/2.1' becomes 'Googlebot'
                )")
      .def("InitUserAgentsAndPath",
           &PublicStatefulRobotsMatcher::InitUserAgentsAndPath,
           py::arg("user_agents").none(false), py::arg("path").none(false),
           R"(
Initialize next path and user-agents to check. Path must contain only the
path, params, and query (if any) of the url and must start with a '/'.
         )")
      .def("seen_any_agent", &PublicStatefulRobotsMatcher::seen_any_agent,
           R"(
Returns true if any user-agent was seen.
         )");
};