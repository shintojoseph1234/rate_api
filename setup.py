#!/usr/bin/env python
import os
from setuptools import find_packages, setup
from pip.req import parse_requirements

# include the readmefile
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()
# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

# reqs is a list of requirement
install_reqs = parse_requirements(os.path.join(os.path.dirname(__file__), 'requirements.txt'))

setup(
    name='rate_API',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Average prices between origin and destination',
    long_description=README,
    install_requires=install_reqs,
    url='https://localhost:8000/',
    author='Shinto Joseph',
    author_email='shintojoseph1234@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
