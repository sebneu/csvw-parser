from setuptools import setup, find_packages

setup(
    name='pycsvw',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'language_tags',
        'rdflib',
        'uritemplate'
    ],
    url='https://github.com/sebneu/csvw-parser',
    license='',
    author='Sebastian Neumaier',
    author_email='sebastian.neumaier@wu.ac.at',
    description='Python implementation of the W3C CSV on the Web specification, cf. http://w3c.github.io/csvw/.'
)
