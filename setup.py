from setuptools import setup, find_packages
from docs.conf import VERSION

setup(
    name='Brewmeister',
    version=VERSION,
    long_description=open('README.rst').read(),
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Babel>=1.3',
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
