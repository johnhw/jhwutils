#!/usr/bin/env python

from distutils.core import setup

setup(name='jhwutils',
      version='1.3.1',
      description='Teaching support utilities',
      author='John H. Williamson',
      author_email='johnhw@gmail.com',
      url='https://github.com/johnhw/jhwutils',
      packages=['jhwutils'],
      include_package_data=True,
      package_data={"jhwutils": ["*.css"]},
     )