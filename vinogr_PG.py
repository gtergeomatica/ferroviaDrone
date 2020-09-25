#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
from sys import argv
import subprocess
import psycopg2

def main():

    # define GRASS Database
    # add your path to grassdata (GRASS GIS database) directory
    #gisdb = os.path.join(os.path.expanduser("~"), "grassdata")
    # the following path is the default path on MS Windows
    gisdb = os.path.join(os.path.expanduser("~"), "/home/ubuntu/grass_DB")

    print(gisdb)
    # specify (existing) Location and Mapset
    location = "wgs84"
    mapset = "casella"

    #grass7bin = r'C:\OSGeo4W64\bin\grass78.bat'
    grass7bin = '/usr/bin/grass'

    # query GRASS GIS itself for its GISBASE
    startcmd = [grass7bin, '--config', 'path']
    try:
        p = subprocess.Popen(startcmd, shell=False,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out)
        out = out.decode('utf-8')
        print(out)
    except OSError as error:
        sys.exit("ERROR: Cannot find GRASS GIS start script"
                 " {cmd}: {error}".format(cmd=startcmd[0], error=error))
    if p.returncode != 0:
        sys.exit("ERROR: Issues running GRASS GIS start script"
                 " {cmd}: {error}"
                 .format(cmd=' '.join(startcmd), error=err))
    gisbase = out.strip(os.linesep)
    print(gisbase)
    # set GISBASE environment variable
    os.environ['GISBASE'] = gisbase

    # define GRASS-Python environment
    grass_pydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(grass_pydir)

    # import (some) GRASS Python bindings
    import grass.script as gscript
    import grass.script.setup as gsetup

    # launch session
    rcfile = gsetup.init(gisbase, gisdb, location, mapset)

    #print(rcfile)

    # example calls
    gscript.message('Current GRASS GIS 7 environment:')
    print (gscript.gisenv())
    
    #import data from postgresDB --> sql query result
    gscript.run_command('v.in.ogr', input="PG:host=192.168.2.28 port=5432 dbname=city_routing user=postgres password=postgresnpwd", layer='output', output='line2d', type='line', overwrite=True)
  

if __name__ == "__main__":
	main()