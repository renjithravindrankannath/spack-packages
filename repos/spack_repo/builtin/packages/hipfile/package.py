# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import os

from spack_repo.builtin.build_systems.cmake import CMakePackage
from spack_repo.builtin.build_systems.rocm import ROCmLibrary, ROCmPackage

from spack.package import *


class Hipfile(ROCmLibrary, CMakePackage):
    """HIP file I/O library for ROCm ecosystem."""

    homepage = "https://github.com/ROCm/rocm-systems"
    git = "https://github.com/ROCm/rocm-systems.git"

    tags = ["rocm"]
    maintainers("srekolam", "renjithravindrankannath", "afzpatel")

    license("MIT")

    rocm_url_map = [
        ("7.2.3", "https://github.com/ROCm/rocm-systems/archive/rocm-{0}.tar.gz"),
        (None, "https://github.com/ROCm/rocm-systems/archive/refs/tags/therock-{1}.{2}.tar.gz"),
    ]

    version("7.14.0", sha256="8cadf0d5c0f53f334b7b940a78619d1746c913b26ae719e2a09e20a6f7128330")  # therock-7.14 tag
    version("7.13.0", sha256="86162d975c59c2f43eb79187378a9b10615db5c1d73441e7e0b7621a7ef8962c")  # therock-7.13 tag
    version("7.2.3", sha256="e90cfd8694af28a56433c8827a581ee12a4ba835f0d952436741d9e0f3f8685b")  # rocm-7.2.3 tag

    amdgpu_targets = ROCmPackage.amdgpu_targets

    variant("rocm", default=True, description="Enable ROCm support")
    variant(
        "amdgpu_target",
        description="AMD GPU architecture",
        values=auto_or_any_combination_of(*amdgpu_targets),
    )

    depends_on("c", type="build")
    depends_on("cxx", type="build")

    depends_on("cmake@3.16.8:", type="build")
    depends_on("util-linux")  # for libmount

    with when("+rocm"):
        for ver in [
            "7.2.3",
            "7.13.0",
            "7.14.0",
        ]:
            depends_on(f"hip@{ver}", when=f"@{ver}")
            depends_on(f"rocm-core@{ver}", when=f"@{ver}")
            depends_on(f"rocminfo@{ver}", when=f"@{ver}")
            depends_on(f"llvm-amdgpu@{ver}", when=f"@{ver}")
            depends_on(f"rocm-cmake@{ver}:", type="build", when=f"@{ver}")

    @property
    def root_cmakelists_dir(self):
        if self.spec.satisfies("@7.13:"):
            return "projects/hipfile"
        else:
            return "rocprofiler-sdk/projects/hipfile"

    def setup_build_environment(self, env: EnvironmentModifications) -> None:
        env.set("HIP_PATH", self.spec["hip"].prefix)
        env.set("ROCM_PATH", self.spec["hip"].prefix)
        env.set("HIP_PLATFORM", "amd")

    def cmake_args(self):
        args = [
            self.define("HIP_PLATFORM", "amd"),
            self.define("HIP_PATH", self.spec["hip"].prefix),
            self.define("ROCM_PATH", self.spec["hip"].prefix),
            self.define("CMAKE_INSTALL_LIBDIR", "lib"),
            self.define("ROCM_VERSION", str(self.spec.version)),
        ]

        if self.spec.satisfies("^cmake@3.21.0:3.21.2"):
            args.append(self.define("__skip_rocmclang", "ON"))

        if "auto" not in self.spec.variants["amdgpu_target"]:
            args.append(self.define_from_variant("GPU_TARGETS", "amdgpu_target"))

        return args
