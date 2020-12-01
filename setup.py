#!/usr/bin/env python3

import os
import re
from io import open

from setuptools import setup, find_packages

with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                       "phoneloc", "__init__.py"), encoding="utf8") as f:
    __version__ = re.search(r'__version__ = "(.*?)"', f.read()).group(1)

setup(
    name='Phoneloc',
    version=__version__,
    description='手机归属地信息库',
    packages=find_packages(exclude=['tests*']),
    package_data={'phoneloc': ['*.csv', 'phone.dat']},
    license='BSD',
)
