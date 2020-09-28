#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
from sys import argv
import subprocess
from os.path import basename


def main():
    gisdb = os.path.join(os.path.expanduser("~"), "/home/ubuntu/grass_DB")

    print(gisdb)
    # specify (existing) Location and Mapset
    location = "wgs84"
    mapset = "casella"
    print('1')
    #grass7bin = r'C:\OSGeo4W64\bin\grass78.bat'
    grass7bin = '/usr/bin/grass'

    # query GRASS GIS itself for its GISBASE
    startcmd = [grass7bin, '--config', 'path']
    # try:
        # p = subprocess.Popen(startcmd, shell=False,
                             # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # out, err = p.communicate()
        # print(out)
        # out = out.decode('utf-8')
        # print(out)
    # except OSError as error:
        # sys.exit("ERROR: Cannot find GRASS GIS start script"
                 # " {cmd}: {error}".format(cmd=startcmd[0], error=error))
    # if p.returncode != 0:
        # sys.exit("ERROR: Issues running GRASS GIS start script"
                # " {cmd}: {error}"
                 # .format(cmd=' '.join(startcmd), error=err))
    # gisbase = out.strip(os.linesep)
    #print(gisbase)
    print('2')
    
    # set GISBASE environment variable
    gisbase = '/usr/lib/grass74'
    os.environ['GISBASE'] = gisbase

    # define GRASS-Python environment
    grass_pydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(grass_pydir)
    
    #print(grass_pydir)

    # import (some) GRASS Python bindings
    import grass.script as gscript
    import grass.script.setup as gsetup
    
    modname = 'grass.script'
    if modname not in sys.modules:
        print('not imported')
    print(sys.modules)
    
    #print("init" in dir(grass.script.setup))
    print(gisbase)
    print(gisdb)
    #print(location)
    print(mapset)
    print(mapset)
    print('ok')

    # launch session
    rcfile = gsetup.init(gisbase, gisdb, location, mapset)
    print(rcfile)
    
    print('session ok')

    # example calls
    #gscript.message('Current GRASS GIS 7 environment:')
    print (gscript.gisenv())
    

if __name__ == "__main__":
	main()
