# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='olap3',
      version='0.2',
      description='Interface to OLAP DBs',
      author='Leonid Kolesnichenko',
      author_email='xperience439@gmail.com',
      packages=find_packages(),
      namespace_packages=['olap3'],
      package_dir={'olap3': 'olap3'},
      package_data={'olap3.resources': ['*.wsdl']},
      install_requires=["setuptools~=60.2.0", "cornice", "webob", "venusian", "zeep"],
      url="https://github.com/robert-werner/olap3",
      license='Apache Software License 2.0',
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Development Status :: 3 - Alpha",
          "Intended Audience :: Developers",
          "Topic :: Software Development :: Libraries :: Python Modules"
      ]
      )
