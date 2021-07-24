#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

thelibFolder = os.path.dirname(os.path.realpath(__file__))

requirementPath = thelibFolder + '/requirements.txt'

install_requires = [] # Here we'll get: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]

if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

setup(name="cq-viewer",
      version='0.1',
      author='Stuart Wichman',
      author_email='stuart.j@wichman-web.org',
      description='WSJT-X Log CQ Visualizer',
      url='https://gitlab.com/swichman/cq-viewer',
      project_urls={
        'Bug Tracker': 'https://gitlab.com/swichman/cq-viewer/-/issues',
      },
      package_dir={"": "cqviewer"},
      packages=find_packages(where="cqviewer"),
      python_requires=">=3",
      install_requires=install_requires)
