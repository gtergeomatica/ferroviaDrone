#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
from sys import argv
import subprocess
import psycopg2

def main():

    #script, lon1, lat1, lon2, lat2, ffile = argv
    script, ffile = argv
    
    #temporary map names
    global tmp
    tmp = {}

    processid = "{:.2f}".format(time.time())
    print(processid)
    processid = processid.replace(".", "_")
    tmp["line3d"] = "line3d_" + processid
    tmp["point3d"] = "point3d_" + processid
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
    line2d = 'genova_casella_edit_wgs84'
    dem = 'dem_20'
    
    #set computational region to vector line
    gscript.run_command('g.region', raster=dem, flags='ap')
    
    #gscript.run_command('v.in.ogr', input="PG:host=192.168.2.28 port=5432 dbname=city_routing user=postgres password=postgresnpwd", layer='output', output='line2d', type='line', overwrite=True)
    
    gscript.run_command('v.drape', input=line2d, type='line', output=tmp["line3d"], elevation=dem, method='bilinear')
    
    if ffile == 'CSV':
        gscript.run_command('v.to.points', input=tmp["line3d"], type='line', output=tmp["point3d"], use='vertex')
        gscript.run_command('v.out.ascii', input=tmp["point3d"], type='point', output='/home/ubuntu/ferroviaDrone/casella.csv', format='point', separator='comma', flags='c', overwrite=True)
    elif ffile == 'KML':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='/home/ubuntu/ferroviaDrone/casella.kml', format='KML')
    elif ffile == 'GML':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='/home/ubuntu/ferroviaDrone/casella.gml', format='GML')
    elif ffile == 'GeoJSON':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='/home/ubuntu/ferroviaDrone/casella.geojson', format='GeoJSON')
    else:
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='/home/ubuntu/ferroviaDrone/casella.shp', format='ESRI_Shapefile')
    

if __name__ == "__main__":
	main()