# -*- coding: utf-8 -*-
"""Setuptools for scd."""


import os.path

import setuptools


REQUIREMENTS = [
    "six>=1.10",
    "packaging>=16,<17",
    "semver>=2,<3",
    "jsonschema>=2.5,<2.6",
    "jinja2>=2.6,<3"
]
"""Requirements for scd project."""


with open(os.path.join(os.path.dirname(__file__), "README.rst"), "rt") as rfp:
    long_description = rfp.read()


setuptools.setup(
    name="scd",
    version="1.1.0",
    description="Something Completely different",
    long_description=long_description,
    author="Sergey Arkhipov",
    author_email="nineseconds@yandex.ru",
    maintainer="Sergey Arkhipov",
    maintainer_email="nineseconds@yandex.ru",
    license="MIT",
    url="https://github.com/9seconds/scd",
    packages=setuptools.find_packages(),
    python_requires=">=2.7",
    install_requires=REQUIREMENTS,
    extras_require={
        "yaml": ["PyYAML ~= 3.10"],
        "toml": ["toml ~= 0.9.2"],
        "simplejson": ["simplejson"],
        "colors": ["colorama>=0.3,<0.4"]
    },
    entry_points={
        "console_scripts": ["scd = scd.main:main"],
        "scd.version": [
            "semver = scd.version:SemVer",
            "pep440 = scd.version:PEP440",
            "git_semver = scd.version:GitSemVer",
            "git_pep440 = scd.version:GitPEP440"
        ]
    },
    zip_safe=True,
    classifiers=(
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development",
        "Topic :: Software Development :: Version Control",
        "Topic :: Utilities"
    )
)
