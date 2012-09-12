from setuptools import setup, find_packages
import os
import sys

install_requires = [
          'setuptools',
          'plone.app.jquerytools',
          # 'Plone', Too confusing for those using releases < 3.2
          'hachoir_core',
          'hachoir_metadata',
          'hachoir_parser',
          'archetypes.schemaextender',
      ]

version = '3.1.1'

tests_require = ['collective.testcaselayer', 'interlude']

if sys.version_info < (2, 6):
    install_requires.append('simplejson')

setup(name='collective.flowplayer',
      version=version,
      description="A simple package using Flowplayer for video and audio content",
      long_description=open("README.rst").read() + "\n\n" +
                       open(os.path.join("docs", "UPGRADE.txt")).read() + "\n\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
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
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      tests_require=tests_require,
      extras_require={'test': tests_require},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
