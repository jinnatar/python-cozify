from distutils.core import setup
from setuptools.command.test import test as TestCommand

import sys
import cozify

with open('README.rst') as file:
        long_description = file.read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)



setup(name='cozify',
        version = cozify.__version__,
        author = 'artanicus',
        author_email = 'python-cozify@nocturnal.fi',
        url = 'https://github.com/Artanicus/python-cozify',
        description = 'Unofficial Python bindings and helpers for the unpublished Cozify API.',
        long_description = long_description,
        license = 'MIT',
        packages = ['cozify'],
	tests_require=['pytest'],
	install_requires=['requests'],
        cmdclass={'test': PyTest},
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: OSI Approved :: MIT License",
            ]
        )
