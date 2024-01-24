#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = [ ]

setup(
    author="Brendan Strejcek",
    author_email='brendan@datagazing.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Import Revel grade data into D2L LMS",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='revel2d2l',
    name='revel2d2l',
    packages=find_packages(include=['revel2d2l', 'revel2d2l.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/datagazing/revel2d2l',
    version='0.1.0',
    zip_safe=False,
)
