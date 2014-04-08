import os
import glob
from setuptools import setup, find_packages


VERSION = '0.1.0dev'


def mo_files():
    linguas = glob.glob('brew/translations/*/LC_MESSAGES/messages.mo')
    lpaths = [os.path.dirname(d) for d in linguas]
    return zip(lpaths, [[l] for l in linguas])


# Data files to be installed after build time
data_files = mo_files()


setup(
    name='Brewmeister',
    version=VERSION,
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    scripts=['bin/brewmeister'],
    data_files=data_files,
    install_requires=[
        'Babel>=1.3',
        'crcmod>=1.7',
        'docutils>=0.11',
        'Flask>=0.10.1',
        'Flask-Babel>=0.9',
        'Flask-Cache>=0.12',
        'Flask-PyMongo>=0.3.0',
        'Flask-Script>=0.6.3',
        'fysom>=1.0.14',
        'jsonschema>=2.3.0',
        'pyserial>=2.7',
        'reportlab>=2.7',
    ]
)
