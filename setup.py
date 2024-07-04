import os
import pathlib
import platform
import subprocess

import pybind11.setup_helpers
import setuptools


def build_robotstxt(
    src: os.PathLike,
    out: os.PathLike,
) -> None:
    src = pathlib.Path(src).resolve()
    out = pathlib.Path(out).resolve()

    subprocess.check_call(
        ("cmake", "-S", str(src), "-B", str(out), "-DROBOTS_INSTALL=OFF")
    )
    subprocess.check_call(("cmake", "--build", str(out)))


def remove_dynamic_libraries(directory: os.PathLike) -> None:
    directory = pathlib.Path(directory).resolve()

    match platform.system():
        case "Linux":
            extensions = (".so",)
        case "Darwin":
            extensions = (".dylib",)
        case "Windows":
            extensions = (".dll", ".lib")
        case _:
            raise Exception("Could not determine your systems platform")

    for path in directory.iterdir():
        if path.is_dir():
            continue
        for suffix in path.suffixes:
            if suffix in extensions:
                path.unlink()


def main() -> None:
    # Build robotstxt
    robotstxt_src = pathlib.Path.cwd() / "robotstxt"
    robotstxt_build = pathlib.Path.cwd() / "c-build"
    if not robotstxt_src.exists():
        raise Exception(f"Could not find robotstxt source in {str(robotstxt_src)}")
    if not any(robotstxt_src.iterdir()):
        raise Exception(
            "The robotstxt directory is empty. "
            "Make sure you have pulled all the submodules as well.\n"
            "\tgit submodules init\n"
            "\tgit submodules update"
        )
    build_robotstxt(robotstxt_src, robotstxt_build)

    # Remove the dynamic libraries to force a static link
    remove_dynamic_libraries(robotstxt_build)

    setuptools.setup(
        ext_modules=[
            pybind11.setup_helpers.Pybind11Extension(
                "pyrobotstxt.googlebot",
                ["./src/pyrobotstxt/googlebot.cc"],
                # Include robotstxt and abseil headers
                include_dirs=[
                    str(robotstxt_src),
                    str(robotstxt_build / "libs/abseil-cpp-src/"),
                ],
                # Include robotstxt and relevant abseil libraries
                libraries=[
                    "robots",
                    "absl_strings",
                    "absl_string_view",
                    "absl_throw_delegate",
                ],
                library_dirs=[
                    str(robotstxt_build),
                    str(robotstxt_build / "libs/abseil-cpp-build/absl/strings"),
                    str(robotstxt_build / "libs/abseil-cpp-build/absl/base"),
                ],
                # Match the robotstxt c++ version.
                #
                # There is a breaking change 14->17 for the dependant absl
                # library. Symbol table miss match with absl::string_view
                # becoming std::string_view.
                cxx_std=14,
            ),
        ],
        cmdclass={"build_ext": pybind11.setup_helpers.build_ext},
    )


main()
