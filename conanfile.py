#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class FlacConan(ConanFile):
    name = "flac"
    version = "1.3.2"
    description = "Free Lossless Audio Codec "
    url = "https://github.com/xiph/flac"
    license = "BSD"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    source_subfolder = "sources"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "use_asm": [True, False]}
    default_options = "shared=False", "use_asm=False"

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
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.md", dst="licenses", keep_path=False)
        self.copy(pattern="COPYING.*", src=self.source_subfolder, dst="licenses", keep_path=False)
        include_dir = os.path.join(self.source_subfolder, "include")
        self.copy(pattern="*.h", dst="include", src=include_dir)
        self.copy(pattern="*.hh", dst="include", src=include_dir)
        self.copy(pattern="*.hpp", dst="include", src=include_dir)
        self.copy(pattern="*.dll", dst="bin", keep_path=False)
        self.copy(pattern="*.lib", dst="lib", keep_path=False)
        self.copy(pattern="*.a", dst="lib", keep_path=False)
        self.copy(pattern="*.so*", dst="lib", keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
