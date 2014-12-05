#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pip.req import parse_requirements

import fallback_storage

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

version = fallback_storage.__version__

readme = open('README.rst').read()

requirements = [str(req.req) for req in parse_requirements('requirements.txt')]

setup(
    name='django-fallback-storage',
    version=version,
    description="""Multiple Storage Engines""",
    long_description=readme,
    author='Piper Merriam',
    author_email='pipermerriam@gmail.com',
    url='https://github.com/simpleenergy/django-fallback-storage',
    packages=[
        'fallback_storage',
    ],
    include_package_data=True,
    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='django-fallback-storage',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
