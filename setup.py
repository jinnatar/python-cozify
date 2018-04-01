from setuptools import setup

import sys
import cozify

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='cozify',
    version=cozify.__version__,
    author='artanicus',
    author_email='python-cozify@nocturnal.fi',
    url='https://github.com/Artanicus/python-cozify',
    description='Unofficial Python3 client library for the Cozify API.',
    long_description=long_description,
    license='MIT',
    packages=['cozify'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=['requests', 'absl-py'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ])
