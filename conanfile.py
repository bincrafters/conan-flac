from conans import ConanFile, CMake, tools
import os


class FlacConan(ConanFile):
    name = "flac"
    description = "Free Lossless Audio Codec"
    homepage = "https://github.com/xiph/flac"
    url = "https://github.com/bincrafters/conan-flac"
    license = ("BSD", "GPL", "LPGL")
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    requires = "ogg/1.3.4"

    _source_subfolder = "source_subfolder"

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def build_requirements(self):
        self.build_requires("nasm/2.14")

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'src', 'libFLAC', 'CMakeLists.txt'),
            'target_link_libraries(FLAC PRIVATE $<$<BOOL:${HAVE_LROUND}>:m>)',
            'target_link_libraries(FLAC PUBLIC $<$<BOOL:${HAVE_LROUND}>:m>)')
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            'add_subdirectory("microbench")',
            '#add_subdirectory("microbench")')
        tools.replace_in_file(
            os.path.join(self._source_subfolder, 'CMakeLists.txt'),
            'set(CMAKE_EXE_LINKER_FLAGS -no-pie)',
            '#set(CMAKE_EXE_LINKER_FLAGS -no-pie)')

    def _configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_EXAMPLES"] = False
        cmake.definitions["BUILD_DOCS"] = False
        cmake.definitions["BUILD_TESTING"] = False
        cmake.configure()
        return cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        cmake = self._configure_cmake()
        cmake.install()
        self.copy(pattern="COPYING.*", dst="licenses", src=self._source_subfolder, keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share"), src=os.path.join(self._source_subfolder, "include", "share"), keep_path=False)
        self.copy(pattern="*.h", dst=os.path.join("include", "share", "grabbag"),
                  src=os.path.join(self._source_subfolder, "include", "share", "grabbag"), keep_path=False)
        tools.rmdir(os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["FLAC__NO_DLL"]
