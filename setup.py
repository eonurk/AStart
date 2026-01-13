from setuptools import setup, Extension, find_packages
import sys
import os

# Define the C++ Extension
# We use a standard Extension, but we won't import it as a module.
# We will find the .so/.dll file and load it with ctypes.
module = Extension(
    'astart._cpp_backend',
    sources=['astart/cpp/solver.cpp'],
    extra_compile_args=['-O3', '-std=c++17'],
    language='c++'
)

setup(
    name="astart",
    version="0.2.0",
    description="Batch A* Algorithm (Python + C++ Optimized)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    ext_modules=[module],
    include_package_data=True,
    zip_safe=False,
)
