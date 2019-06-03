# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
from conans.errors import ConanException
import os


class GccConan(ConanFile):
    name = "gcc"
    version = "9.1.0"
    description = "The GNU Compiler Collection includes front ends for C, C++, Objective-C, Fortran, Ada, Go, " \
                  "and D, as well as libraries for these languages (libstdc++,...)"
    topics = ("conan", "gcc", "logging")
    url = "https://github.com/bincrafters/conan-gcc"
    homepage = "https://gcc.gnu.org/"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "GPL-3.0-or-later"
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False], "languages": "ANY"}
    default_options = {"shared": False, "fPIC": True, "languages": "c,c++"}
    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"
    no_copy_source = True

    requires = ("gmp/6.1.2@bincrafters/stable",
                "mpfr/4.0.2@bincrafters/stable",
                "mpc/1.1.0@bincrafters/stable",
                "zlib/1.2.11@conan/stable")

    def config_options(self):
        if self.settings.os == 'Windows':
            del self.options.fPIC

    def source(self):
        # https://gcc.gnu.org/mirrors.html
        mirrors = ["ftp://ftp.gnu.org/gnu/gcc",
                   "ftp://ftp.lip6.fr/pub/gcc/releases",
                   "ftp://ftp.irisa.fr/pub/mirrors/gcc.gnu.org/gcc/releases/",
                   "ftp://ftp.uvsq.fr/pub/gcc/releases/",
                   "http://mirrors-usa.go-parts.com/gcc/releases/",
                   "http://mirrors.concertpass.com/gcc/releases/"]
        for mirror in mirrors:
            try:
                source_url = mirror + "/{n}-{v}/{n}-{v}.tar.gz".format(n=self.name, v=self.version)
                tools.get(source_url, sha256="be303f7a8292982a35381489f5a9178603cbe9a4715ee4fa4a815d6bcd2b658d")
                break
            except ConanException:
                pass
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def build(self):
        libdir = "%s/lib/gcc/%s" % (self.package_folder, self.version)
        tools.replace_in_file(os.path.join(self.source_folder,
                                           self._source_subfolder, "gcc", "config", "i386", "t-linux64"),
                              "m64=../lib64", "m64=../lib", strict=False)
        tools.replace_in_file(os.path.join(self.source_folder,
                                           self._source_subfolder, "libgcc", "config", "t-slibgcc-darwin"),
                              "@shlib_slibdir@", libdir, strict=False)

        pkgversion = "Conan GCC %s" % self.version
        tools.mkdir(self._build_subfolder)
        condigure_dir = os.path.abspath(os.path.join(self.source_folder, self._source_subfolder))
        with tools.chdir(self._build_subfolder):
            # http://www.linuxfromscratch.org/lfs/view/development/chapter06/gcc.html
            args = ["--enable-languages=%s" % self.options.languages,
                    "--disable-nls",
                    "--disable-bootstrap",
                    "--disable-multilib",  # this means building two architectures at once, too hard for now
                    "--with-system-zlib",
                    "--program-suffix=-%s" % self.version,
                    "--with-bugurl=https://github.com/bincrafters/community/issues",
                    "--with-pkgversion=%s" % pkgversion,
                    "--libdir=%s" % libdir,
                    "--with-gmp=%s" % self.deps_cpp_info["gmp"].rootpath,
                    "--with-mpfr=%s" % self.deps_cpp_info["mpfr"].rootpath,
                    "--with-mpc=%s" % self.deps_cpp_info["mpc"].rootpath]
            if self.settings.os == "Macos":
                # https://github.com/Homebrew/homebrew-core/blob/master/Formula/gcc.rb
                args.extend(["--with-native-system-header-dir=/usr/include",
                             "--with-sysroot=/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk"])
            env_build = AutoToolsBuildEnvironment(self)
            env_build.libs = []  # otherwise causes config.log to fail finding -lmpc
            if self.settings.compiler in ["clang", "apple-clang"]:  # GCC doesn't like Clang-specific flags
                if self.settings.compiler.libcxx == "libc++":
                    env_build.cxx_flags.remove("-stdlib=libc++")
                elif self.settings.compiler.libcxx in ["libstdc++", "libstdc++11"]:
                    env_build.cxx_flags.remove("-stdlib=libstdc++")
            env_build.configure(args=args, configure_dir=condigure_dir)
            make_args = []
            if self.settings.os == "Macos":
                #  Ensure correct install names when linking against libgcc_s;
                #  see discussion in https://github.com/Homebrew/legacy-homebrew/pull/34303
                make_args.append("BOOT_LDFLAGS=-Wl,-headerpad_max_install_names")
            env_build.make(args=make_args)
            env_build.install()

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._source_subfolder)

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH env var with : " + bindir)
        self.env_info.PATH.append(bindir)

        cc = os.path.join(bindir, "gcc-%s" % self.version)
        self.output.info("Appending CC env var with : " + cc)
        self.env_info.CC = cc

        cxx = os.path.join(bindir, "g++-%s" % self.version)
        self.output.info("Appending CXX env var with : " + cxx)
        self.env_info.CXX = cxx
