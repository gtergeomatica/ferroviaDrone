#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
from sys import argv
import subprocess
from os.path import basename
from grass_session import Session
from grass.script import core as gcore


def main():
    with Session(gisdb="/home/ubuntu/grass_DB", location="wgs84",
                 mapset="casella"):
       # run something in PERMANENT mapset:
       print(gcore.parse_command("g.gisenv", flags="s"))
    

if __name__ == "__main__":
	main()
