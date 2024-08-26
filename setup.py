from setuptools import setup, find_packages
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

# Import the app to retrieve the version
sys.path.insert(0, here)
from pywrite.src import __version__

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pywrite',  # The correct package name
    version=__version__,
    description='RCON communication tool for Minecraft servers.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Alex Woodward',
    author_email='contact@tawoodward.com',
    url='https://github.com/alex-woodward/pywrite',
    download_url=f'https://github.com/alex-woodward/pywrite/archive/v{__version__}.tar.gz',
    packages=find_packages(exclude=["tests", "tests.*"], include=['pywrite', 'pywrite.*']),
    package_data={
        '': ['*.conf'],
        'pywrite': ['py.typed']
    },
    extras_require={
        'test': ['mypy', 'coverage'],
        'dev': ['mypy', 'ipdb', 'autopep8', 'coverage']
    },
    python_requires='>=3.7',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    keywords=['rcon', 'minecraft'],
)
