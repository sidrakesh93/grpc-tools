"""A setup module for the GRPC packager-unittest service.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import setuptools

from setuptools import setup, find_packages

install_requires = [
  'oauth2client>=0.4.1',
  'grpc>=0.9.0a0'
]

setuptools.setup(
  name='packager-unittest-v2',
  version='1.0.0',

  author='Google Inc',
  author_email='googleapis-packages@google.com',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: APIs',
    'Programming Language :: Python :: 2.7'
  ],
  description='GRPC library for service packager-unittest-v2',
  install_requires=install_requires,
  license='Apache',
  packages=find_packages(),
  url='https://github.com/google/googleapis'
)
