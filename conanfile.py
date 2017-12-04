#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, VisualStudioBuildEnvironment, tools
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

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("nasm/2.13.01@conan/stable")

    def requirements(self):
        self.requires("ogg/1.3.3@bincrafters/stable")

    def source(self):
        source_url = "http://downloads.xiph.org/releases/flac/"
        tools.download("{0}/flac-{1}.tar.xz".format(source_url, self.version),
                       "flac.tar.xz")
        self.run("cmake -E tar xf flac.tar.xz")
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, "sources")

    def unix_build(self):
        build_env = AutoToolsBuildEnvironment(self)
        build_env.include_paths = self.deps_cpp_info.includedirs
        with tools.chdir("sources"):
            build_env.configure()
            build_env.make()

    def windows_build(self):
        import fnmatch
        vcxprojs = []
        for root, dirnames, filenames in os.walk("sources"):
            for filename in fnmatch.filter(filenames, "*.vcxproj"):
                vcxprojs.append(os.path.join(root, filename))
        patterns = (
            r"$(SolutionDir)objs\$(Platform)\$(Configuration)\lib\libogg_static.lib",
            r"$(SolutionDir)objs\$(Configuration)\lib\libogg_static.lib"
        )
        for proj in vcxprojs:
            self.output.info("Patching " + proj)
            for pattern in patterns:
                tools.replace_in_file(proj, pattern, "ogg.lib", strict=False)
        postfix = "_dynamic" if self.options.shared else "_static"
        targets = ["flac", "libFLAC"+postfix, "libFLAC++"+postfix, 
                   "getopt_static", "grabbag_static", "replaygain_analysis_static", 
                   "replaygain_synthesis_static", "utf8_static", 
                   "win_utf8_io_static"]
        env_build = VisualStudioBuildEnvironment(self)
        env_build.include_paths.extend(self.deps_cpp_info.include_paths)
        env_build.lib_paths.extend(self.deps_cpp_info.lib_paths)
        bvars = dict(env_build.vars)
        bvars.update({"UseEnv": "true"})
        with tools.environment_append(bvars), tools.chdir("sources"):
            cmd = tools.msvc_build_command(self.settings, "flac.sln", targets=targets)
            print(cmd)
            self.run(cmd)

    def build(self):
        if self.settings.os != "Windows":
            self.unix_build()
        else:
            self.windows_build()

    def package(self):
        self.copy(pattern="*.h", dst="include", src="sources/include")
        self.copy(pattern="*.hh", dst="include", src="sources/include")
        self.copy(pattern="*.hpp", dst="include", src="sources/include")
        with tools.chdir("sources"):
            self.copy(pattern="LICENSE")
            self.copy(pattern="*.dll", dst="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
