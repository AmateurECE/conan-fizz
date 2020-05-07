from conans import ConanFile, CMake, tools
import shutil
import glob


class ConanFizz(ConanFile):
    name = "fizz"
    version = "2020.02.17.00"
    license = "BSD"
    author = "Ethan D. Twardy <edtwardy@mtu.edu>"
    url = "https://github.com/AmateurECE/conan-fizz"
    description = """Fizz is a TLS 1.3 implementation.
    Fizz currently supports TLS 1.3 drafts 28, 26 (both wire-compatible with
    the final specification), and 23. All major handshake modes are supported,
    including PSK resumption, early data, client authentication, and
    HelloRetryRequest."""
    topics = ("facebook", "tls", "networking")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}
    generators = "cmake_find_package"
    build_requires = "fmt/6.2.0"
    requires = "openssl/1.1.1d", "libsodium/1.0.18", \
        "folly/2019.10.21.00"

    def source(self):
        self.run("git clone https://github.com/facebookincubator/fizz")
        self.run("git --git-dir=fizz/.git --work-tree=fizz checkout v{}"
                 .format(self.version))

    def build(self):
        # Copy the Find<Package> files to fizz's cmake directory
        for findPackageFile in glob.glob("Find*"):
            shutil.copyfile(findPackageFile, "fizz/fizz/cmake/"
                            + findPackageFile)

        with open("fizz/fizz/CMakeLists.txt") as oldFile, \
             open("CMakeLists.txt.new", "w") as newFile:
            for line in oldFile:
                if line[:-1] == "  find_package(Folly MODULE REQUIRED)":
                    newFile.write("  find_package(folly REQUIRED)\n")
                elif line[:-1] == "find_package(fmt CONFIG REQUIRED)":
                    newFile.write("find_package(fmt REQUIRED)\n")
                elif "FOLLY" in line:
                    newFile.write(line.replace("FOLLY", "folly"))
                else:
                    newFile.write(line)

        shutil.copyfile("CMakeLists.txt.new", "fizz/fizz/CMakeLists.txt")

        cmake = CMake(self)
        cmake.configure(source_folder="fizz/fizz", build_folder="fizz/build")
        cmake.build()
        cmake.test()

    def package(self):
        self.copy("*.h", dst="include/fizz", src="fizz/fizz",
                  excludes=("*Test*", "*test*"))
        self.copy("*fizz.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False, excludes=("*test*"))
        self.copy("*.so", dst="lib", keep_path=False, excludes=("*test*"))
        self.copy("*.dylib", dst="lib", keep_path=False, excludes=("*test*"))
        self.copy("*.a", dst="lib", keep_path=False, excludes=("*test*"))
        self.copy("fizz", dst="bin", src="fizz/build/bin", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["fizz"]

