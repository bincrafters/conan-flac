from conans import ConanFile, CMake, tools
import os


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        test_package_dir = os.path.dirname(os.path.abspath(__file__))
        self.copy("sample.wav", src=test_package_dir, dst=".")

    def test(self):
        if not tools.cross_building(self.settings):
            args = " sample.wav sample.flac"
            bin_path = os.path.join("bin", "test_package")
            self.run(bin_path + args, run_environment=True)
