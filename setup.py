import os
from setuptools import setup, find_packages


setup(
    name='Brewmeister',
    version='0.2.0',
    long_description=open('README.rst').read(),
    packages=find_packages(),
    zip_safe=False,
    scripts=['bin/brewmeister'],
    install_requires=[
        'crcmod>=1.7',
        'Flask>=0.10.1',
        'Flask-RESTful>=0.3.5',
        'pyserial>=3.2.1',
    ]
)
