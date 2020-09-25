#!/usr/bin/env python
# coding=utf-8

import os
from os.path import basename
from zipfile import ZipFile
from sys import argv

script, lon1, lat1, lon2, lat2, ffile = argv

print(lon1 + ", " + lat1 + ", " + lon2 + ", " + lat2 + ", " + ffile)