from distutils.core import setup


with open('README.md') as file:
        long_description = file.read()

setup(name='cozify',
        version = '0.2.3',
        author = 'artanicus',
        author_email = 'python-cozify@nocturnal.fi',
        url = 'https://github.com/Artanicus/python-cozify',
        description = 'Unofficial Python bindings and helpers for the unpublished Cozify API.',
        long_description = long_description,
        license = 'MIT',
        packages = ['cozify'],
        classifiers = [
            "Development Status :: 3 - Alpha",
            "Topic :: Utilities",
            "License :: OSI Approved :: MIT License",
            ]
        )
