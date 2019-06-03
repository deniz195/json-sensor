# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='json-sensor',
    version='0.1.1',
    description='A mini-framework that helps to read data from sensors in a distributed system or machine.',
    long_description=readme,
    author='Deniz Bozyigit',
    author_email='deniz195@gmail.com',
    url='https://github.com/deniz195/json-sensor',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)
