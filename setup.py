# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

import os
import sys


def read(*paths):
    return open(os.path.join(os.path.dirname(__file__), *paths), 'r').read()

version = '4.0'

install_requires = [
    'setuptools',
    'plone.app.jquerytools',
    # 'Plone', Too confusing for those using releases < 3.2
    'hachoir_core',
    'hachoir_metadata',
    'hachoir_parser',
    'archetypes.schemaextender',
]

if sys.version_info < (2, 6):
    install_requires.append('simplejson')

setup(name='collective.flowplayer',
      version=version,
      description="A simple package using Flowplayer for video and audio " +
                  "content",
      long_description='\n\n'.join([
          read("README.rst"),
          read("docs", "UPGRADE.txt"),
          read("docs", "HISTORY.txt"),
      ]),
      # Get more strings from
      # http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Framework :: Plone",
          "Programming Language :: Python",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='flv flash video plone',
      author='Martin Aspeli',
      author_email='optilude@gmail.com',
      url='http://plone.org/products/collective-flowplayer',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      extras_require={
          'test': [
              'plone.app.testing >= 4.2.2',
          ],
      },
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
