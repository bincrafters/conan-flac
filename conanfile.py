#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class FlacConan(ConanFile):
    name = "flac"
    version = "1.3.2"
    url = "https://github.com/xiph/flac"
    description = "Free Lossless Audio Codec "
    license = "https://github.com/xiph/flac/blob/master/COPYING.Xiph"
    exports_sources = ["CMakeLists.txt", "LICENSE"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    generators = "cmake"

    def requirements(self):
        self.requires("ogg/1.3.3@bincrafters/stable")

    def source(self):
        source_url = "http://downloads.xiph.org/releases/flac/"
        tools.download("{0}/flac-{1}.tar.xz".format(source_url, self.version),
                       "flac.tar.xz")
        self.run("cmake -E tar xf flac.tar.xz")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")
        #Rename to "sources" is a convention to simplify later steps

    def build(self):
        build_env = AutoToolsBuildEnvironment(self)
        build_env.include_paths = self.deps_cpp_info.includedirs
        # build_env.cxx_flags.extend(
        #     ["-I{}".format(f) for f in build_env.include_paths])
        with tools.chdir("sources"):
            build_env.configure()
            build_env.make()

    def package(self):
        self.copy(pattern="*.h", dst="include", src="sources/include")
        self.copy(pattern="*.hh", dst="include", src="sources/include")
        self.copy(pattern="*.hpp", dst="include", src="sources/include")
        with tools.chdir("sources"):
            self.copy(pattern="LICENSE")
            self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
