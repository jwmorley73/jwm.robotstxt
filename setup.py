import os
import pathlib
import subprocess

import pybind11.setup_helpers
import setuptools


def build_robotstxt(
    src: os.PathLike,
    out: os.PathLike,
) -> None:
    src = pathlib.Path(src).resolve()
    out = pathlib.Path(out).resolve()

    subprocess.check_call(("cmake", "-S", str(src), "-B", str(out)))
    subprocess.check_call(("cmake", "--build", str(out)))

def main() -> None:
    # Build robotstxt
    robotstxt_src = pathlib.Path.cwd() / "robotstxt"
    if not robotstxt_src.exists():
        raise Exception(
            f"Could not find robotstxt source in {str(robotstxt_src)}"
        )
    robotstxt_build = pathlib.Path.cwd() / "c-build"
    build_robotstxt(robotstxt_src, robotstxt_build)

    # Remove the dynamic library to force a static link
    dynamic_robots_library = robotstxt_build / "librobots.so"
    dynamic_robots_library.unlink()

    # Find the required 3rd party absl headers fetched by robotstxts build
    abseil_src = next(robotstxt_build.rglob("abseil-cpp-src/"), None)
    if abseil_src is None:
        raise Exception("Could not find absl src in robotstxt build")

    setuptools.setup(
        ext_modules=[
            pybind11.setup_helpers.Pybind11Extension(
                "pyrobotstxt.googlebot",
                ["./src/pyrobotstxt/googlebot.cc"],
                # Include robotstxt and abseil headers
                include_dirs=[str(robotstxt_src), str(abseil_src)],
                # Include robotstxt and relevant absl libraries
                libraries=[
                    "robots",
                    "absl_strings",
                    "absl_string_view",
                    "absl_throw_delegate"
                ],
                library_dirs=[
                    str(robotstxt_build),
                    str(robotstxt_build / "libs/abseil-cpp-build/absl/strings"),
                    str(robotstxt_build / "libs/abseil-cpp-build/absl/base")
                ],
                # Match the robotstxt c++ version.
                #
                # There is a breaking change 14->17 for the dependant absl
                # library. Symbol table miss match with absl::string_view
                # becoming std::string_view.
                cxx_std=14
            ),
        ],
        cmdclass={"build_ext": pybind11.setup_helpers.build_ext},
    )

main()
