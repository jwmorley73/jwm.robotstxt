import os
import pathlib
import platform
import shutil
import subprocess
import typing

import pybind11.setup_helpers
import setuptools


def cmake_build(
    src: os.PathLike,
    out: os.PathLike,
    *,
    make_args: typing.Tuple = (),
    build_args: typing.Tuple = (),
) -> None:
    src = pathlib.Path(src).resolve()
    out = pathlib.Path(out).resolve()

    subprocess.check_call(("cmake", "-S", str(src), "-B", str(out), *make_args))
    subprocess.check_call(("cmake", "--build", str(out), *build_args))


def collect_static_libraries(
    libraries: typing.Iterable[str],
    build_directory: os.PathLike,
    lib_directory: os.PathLike,
) -> None:
    build_directory = pathlib.Path(build_directory).resolve()
    lib_directory = pathlib.Path(lib_directory).resolve()
    lib_directory.mkdir(exist_ok=True)

    platform_static_library_suffixes = (".a",)
    if platform.system() == "Windows":
        platform_static_library_suffixes = (".lib",)

    for path in build_directory.rglob("*"):
        if path.suffix not in platform_static_library_suffixes:
            continue
        if path.stem in libraries:
            shutil.copy(path, lib_directory)


def main() -> None:
    # Config
    src_dir = pathlib.Path.cwd() / "robotstxt"
    build_dir = pathlib.Path.cwd() / "c-build"
    lib_dir = pathlib.Path.cwd() / "lib"

    package_name = "pyrobotstxt.googlebot"
    extension_sources = ["./src/pyrobotstxt/googlebot.cc"]
    header_dirs = [
        str(src_dir),
        str(build_dir / "libs/abseil-cpp-src/"),
    ]
    libs = [
        "robots",
        "absl_string_view",
        "absl_strings",
        "absl_throw_delegate",
    ]

    # Check config
    if not src_dir.exists():
        raise FileNotFoundError(f"Could not find robotstxt source in {str(src_dir)}")
    if not any(src_dir.iterdir()):
        raise FileNotFoundError(
            "The robotstxt directory is empty. "
            "Make sure you have pulled all the submodules as well.\n"
            "\tgit submodules init\n"
            "\tgit submodules update"
        )

    # Build and extract libs
    cmake_build(
        src_dir,
        build_dir,
        make_args=(
            "-DROBOTS_INSTALL=OFF",
        ),
        build_args=(
            "--config",
            "Release",
        )
    )
    collect_static_libraries(libs, build_dir, lib_dir)

    setuptools.setup(
        ext_modules=[
            pybind11.setup_helpers.Pybind11Extension(
                name=package_name,
                sources=extension_sources,
                include_dirs=header_dirs,
                libraries=libs,
                library_dirs=[str(lib_dir)],
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
