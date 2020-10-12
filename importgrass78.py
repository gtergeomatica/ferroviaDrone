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
    grass7bin = 'grass78'

    # query GRASS GIS itself for its GISBASE
    startcmd = [grass7bin, '--config', 'path']
    print('2')
    
    # set GISBASE environment variable
    gisbase = '/usr/local/grass78'
    # p = subprocess.Popen(startcmd, shell=False,
                     # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = p.communicate()
    # if p.returncode != 0:
        # print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
        # sys.exit(-1)
    # gisbase = out.strip('\n\r')
    
    os.environ['GISBASE'] = gisbase
    os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
    # add path to GRASS addons
    home = os.path.expanduser("~")
    print('la mia{}'.format(home))
    os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
    print(os.environ['PATH'])

    # define GRASS-Python environment
    gpydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(gpydir)
    
    os.environ['GISDBASE'] = gisdb
    
    #print(grass_pydir)

    # import (some) GRASS Python bindings
    import grass.script as gscript
    import grass.script.setup as gsetup
    
    modname = 'grass.script'
    if modname not in sys.modules:
        print('not imported')
    #print(sys.modules)
    
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
