from distutils.core import setup


with open('README.md') as file:
        long_description = file.read()

setup(name='cozify',
        version='0.1',
        author='artanicus',
        author_email='python-cozify@nocturnal.fi',
        url='https://github.com/Artanicus/python-cozify',
        long_description=long_description,
        )
