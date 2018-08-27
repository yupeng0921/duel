#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='duel',
    version='0.0.1',
    author='yupeng',
    author_email='yupeng0921@gmail.com',
    license='MIT',
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ),
    keywords='duel',
    packages=find_packages(exclude=['tests*']),
    entry_points={
        'console_scripts': [
            'duel=duel:main',
        ],
    },
)
