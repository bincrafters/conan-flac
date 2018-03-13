#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class FlacConan(ConanFile):
    name = "flac"
    version = "1.3.2"
    description = "Free Lossless Audio Codec"
    homepage = "https://github.com/xiph/flac"
    url = "https://github.com/bincrafters/conan-flac"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "sources"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "use_asm": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "use_asm=False", "fPIC=True"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def build_requirements(self):
        if self.options.use_asm:
            self.build_requires("nasm/2.13.01@conan/stable")

    def requirements(self):
        self.requires("ogg/1.3.3@bincrafters/stable")

    def source(self):
        source_url = "http://downloads.xiph.org/releases/flac/"
        tools.download("{0}/flac-{1}.tar.xz".format(source_url, self.version),
                       "flac.tar.xz")
        self.run("cmake -E tar xf flac.tar.xz")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_ARCH"] = str(self.settings.arch)
        cmake.definitions["USE_ASM"] = "ON" if self.options.use_asm else "OFF"

        if self.settings.os != "Windows":
            cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC

        cmake.configure()
        cmake.build()
        cmake.install()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", keep_path=False)
        self.copy(pattern="COPYING.*", src=self.source_subfolder, dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
