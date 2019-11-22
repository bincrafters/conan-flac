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
    _source_subfolder = "sources"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "use_asm": [True, False], "fPIC": [True, False]}
    default_options = {'shared': False, 'use_asm': False, 'fPIC': True}
    requires = "ogg/1.3.3@bincrafters/stable"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def build_requirements(self):
        if self.options.use_asm:
            self.build_requires("nasm/2.13.02")

    def source(self):
        tools.get("{0}/archive/{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["CONAN_ARCH"] = str(self.settings.arch)
        cmake.definitions["USE_ASM"] = self.options.use_asm
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
