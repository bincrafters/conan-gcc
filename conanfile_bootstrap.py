# -*- coding: utf-8 -*-

from conanfile_base import ConanFileBase


class GccBootstrapConan(ConanFileBase):
    name = "gcc-bootstrap"
    version = ConanFileBase.version
    exports = ConanFileBase.exports + ["conanfile_base.py"]

    @property
    def _make_args(self):
        return ["all-gcc"]

    @property
    def _make_install_args(self):
        return ["install-gcc"]

    @property
    def _extra_configure_flags(self):
        return ["--disable-headers",
                "--enable-newlib",
                "--disable-decimal-float",
                "--disable-threads",
                "--disable-libatomic",
                "--disable-libgomp",
                "--disable-libmpx",
                "--disable-libquadmath",
                "--disable-libssp",
                "--disable-libvtv",
                "--disable-libstdcxx"]
