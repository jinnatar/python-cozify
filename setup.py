from setuptools import setup

import sys
import cozify

with open('README.rst') as file:
    long_description = file.read()

setup(
    name='cozify',
    version=cozify.__version__,
    python_requires='>=3.6',
    author='artanicus',
    author_email='python-cozify@nocturnal.fi',
    url='https://github.com/Artanicus/python-cozify',
    project_urls={"Documentation": "https://python-cozify.readthedocs.io/"},
    description='Unofficial Python3 client library for the Cozify API.',
    long_description=long_description,
    license='MIT',
    packages=['cozify'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    install_requires=['requests', 'absl-py'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ])  # yapf: disable
