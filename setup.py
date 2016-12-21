# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = [
    "six>=1.10",
    "packaging>=16,<17",
    "semver>=2,<3",
    "jsonschema>=2.5,<2.6",
    "jinja2>=2.6,<3"
    "colorama>=0.3,<0.4"
]
"""Requirements for scd project."""


setuptools.setup(
    name="scd",
    version="0.1.0",
    description="Something Completely different",
    long_description="",
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
        "simplejson": ["simplejson"]
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
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
        "Programming Language :: Python :: PyPy"
    )
)
