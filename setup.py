#!/usr/bin/python

from setuptools import setup

setup(name='slo_hash',
      version='0.0.1',
      author='SwiftStack',
      packages=['slo_hash'],
      entry_points={
          'paste.filter_factory': [
              'slo_hash=slo_hash:filter_factory',
          ],
      })
