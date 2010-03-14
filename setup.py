from setuptools import setup, find_packages
import os

version = '3.0b7'

tests_require = ['collective.testcaselayer']

setup(name='collective.flowplayer',
      version=version,
      description="A simple package using Flowplayer for video content",
      long_description=open("README.txt").read() + "\n\n" +
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
      url='http://plone.org',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'simplejson',
          'plone.app.jquerytools',
          # 'Plone', Too confusing for those using releases < 3.2
      ],
      tests_require=tests_require,
      extras_require={'tests': tests_require},
      entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
