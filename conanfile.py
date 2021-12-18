from conans import tools
from conanfile_base import ConanFileBase
import os


class GccConan(ConanFileBase):
    name = "gcc"
    version = ConanFileBase.version
    exports = ConanFileBase.exports + ["conanfile_base.py"]

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

    def build_requirements(self):
        if self.options.target or tools.cross_building(self):
            self.build_requires("binutils/2.32@bincrafters/testing")

    @property
    def _make_args(self):
        return ["all-gcc"]

    @property
    def _make_install_args(self):
        return ["install-gcc"]
