import os
import pathlib
import platform
import shutil
import subprocess
import typing

import pybind11.setup_helpers
import setuptools


def cmake_build(
    src_dir: os.PathLike,
    out_dir: os.PathLike,
    *,
    make_args: typing.Tuple = (),
    build_args: typing.Tuple = (),
) -> None:
    src_dir = pathlib.Path(src_dir).resolve()
    out_dir = pathlib.Path(out_dir).resolve()

    subprocess.check_call(("cmake", "-S", str(src_dir), "-B", str(out_dir), *make_args))
    subprocess.check_call(("cmake", "--build", str(out_dir), *build_args))


def collect_static_libraries(
    libs: typing.Iterable[str],
    build_dir: os.PathLike,
    lib_dir: os.PathLike,
) -> None:
    build_dir = pathlib.Path(build_dir).resolve()
    lib_dir = pathlib.Path(lib_dir).resolve()
    lib_dir.mkdir(exist_ok=True)

    prefix = "lib"
    suffix = ".a"
    if platform.system() == "Windows":
        prefix = ""
        suffix = ".lib"

    for path in build_dir.rglob(f"{prefix}*{suffix}"):
        if path.name[len(prefix) : -len(suffix)] in libs:
            shutil.copy(path, lib_dir)


def main() -> None:
    # Config
    src_dir = pathlib.Path.cwd() / "robotstxt"
    build_dir = pathlib.Path.cwd() / "c-build"
    lib_dir = pathlib.Path.cwd() / "lib"

    package_name = "jwm.robotstxt.googlebot"
    extension_sources = ["./src/jwm/robotstxt/googlebot.cc"]
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
            "\tgit submodules update --init --recursive"
        )

    # Build and extract libs
    cmake_build(
        src_dir,
        build_dir,
        make_args=("-DROBOTS_INSTALL=OFF",),
        build_args=(
            "--config",
            "Release",
        ),
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
