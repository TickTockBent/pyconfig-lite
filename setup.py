"""
Setup file for pyconfig-lite.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyconfig-lite",
    version="0.2.0",
    author="TickTockBent",
    author_email="benttick@gmail.com",
    description="A minimal, flexible Python configuration loader with environment variable support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TickTockBent/pyconfig-lite",
    packages=find_packages(),
    package_data={"pyconfig_lite": ["py.typed"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "yaml": ["PyYAML"],
        "toml": ["toml"],
        "all": ["PyYAML", "toml"],
    },
)