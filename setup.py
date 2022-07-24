#!/usr/bin/env python

from os.path import abspath, join, dirname
from setuptools import find_packages, setup

# To use a consistent encoding
from codecs import open
from os import path

# The directory containing this file
HERE = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# Version number typically updated by running `invoke set-version <version>`.
# Run `invoke --help set-version` or see tasks.py for details.
VERSION = '0.1.8'

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3
Programming Language :: Python :: 3 :: Only
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Programming Language :: Python :: 3.9
Programming Language :: Python :: 3.10
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Topic :: Software Development :: Testing
Topic :: Software Development :: Testing :: Acceptance
Topic :: Software Development :: Testing :: BDD
Framework :: Robot Framework
""".strip().splitlines()
DESCRIPTION = ('通用后台分布式测试库 '
               '集成多种测试工具及整合各种后台命令')
KEYWORDS = ('dt4test automation testautomation rpa '
            'testing acceptancetesting atdd bdd')
PACKAGE_DATA = [join('webui', directory, pattern)
                for directory in ('rebot', 'libdoc', 'testdoc', 'lib', 'common')
                for pattern in ('*.html', '*.css', '*.js')]


setup(
    name         = 'dt4test',
    version      = VERSION,
    author       = 'wentao ma',
    author_email = 'mawentao119@gmail.com',
    url          = 'https://dt4test.readthedocs.io/',
    download_url = 'https://pypi.org/project/dt4test/',
    license      = 'Apache License 2.0',
    description  = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    long_description_content_type = 'text/markdown',
    keywords     = KEYWORDS,
    platforms    = 'any',
    python_requires='>=3.6',
    classifiers  = CLASSIFIERS,
    package_dir  = {'': 'src'},
    include_package_data = True,
    packages     = find_packages('src'),
    scripts=['src/dt4test/bin/dt'],
    install_requires=[
        "pytest",
        "jmespath",
        "paramiko",
        "robotframework",
        "kazoo",
        "pyyaml"
    ]
)

# package_data = {'dt4test': PACKAGE_DATA},