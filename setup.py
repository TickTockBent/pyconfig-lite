"""
Setup file for pyconfig-lite.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pyconfig-lite",
    version="0.1.0",
    author="Python Developer",
    author_email="example@example.com",
    description="A minimal, flexible Python configuration loader with environment variable support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pyconfig-lite",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "yaml": ["PyYAML"],
        "toml": ["toml"],
        "all": ["PyYAML", "toml"],
    },
)