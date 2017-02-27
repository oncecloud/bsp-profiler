from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='hadoop-optimizer',
      version=version,
      description="Hadoop optimizer RESTful service",
      long_description="""\
Hadoop optimizer RESTful service""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='hadoop optimizer',
      author='Frank Wu',
      author_email='wuyuewen@otcaix.iscas.ac.cn',
      url='',
      license='Apache License 2',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
