#! ../env/bin/python

import os
import sys
import articlefoundry

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

README = open('README.rst').read()
LICENSE = open("LICENSE").read()

requires = [
    "lxml",
]

setup(
    name='articlefoundry',
    version=articlefoundry.__version__,
    description='A toolkit for manipulating Ambra article objects.',
    long_description=(README),
    license=LICENSE,
    author='Jack LaBarba',
    author_email='jlabarba@plos.org',
    url='http://github/PLOS-Web/articlefoundry',
    install_requires=requires,
    packages=[],
    include_package_data=True,
    scripts=[''],
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
    ),
    keywords='python, ambra, article, archive',
    tests_require=['nose'],
    test_suite='tests',
)
