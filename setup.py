# -*- coding: utf-8 -*-


import setuptools


REQUIREMENTS = [
    "six >= 1.10"
]
"""Requirements for scd project."""


setuptools.setup(
    name="scd",
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
        "console_scripts": ["scd = scd.main:main"]
    },
    setup_requires=["setuptools_scm"],
    use_scm_version={"root": ".", "relative_to": __file__},
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
    )
)
