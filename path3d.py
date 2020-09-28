#!/usr/bin/env python
# coding=utf-8

import os
import sys
import time
from sys import argv
import subprocess
import psycopg2
from os.path import basename
from zipfile import ZipFile
from conn import *

def main():

    script, lon1, lat1, lon2, lat2, ffile = argv
    #script, ffile = argv
    print('sono in def')
    
    outdir0 = os.path.dirname(os.path.realpath(__file__))
    outdir='{}/output3d'.format(outdir0)
    #outdir = '/home/ubuntu/ferroviaDrone/output3d'
    print(outdir)
    for path in os.listdir(outdir):
        full_path = os.path.join(outdir, path)
        if os.path.isfile(full_path):
            os.remove(full_path)
    #print('file eliminati')
    #per far si che elimini lo zip forse bisogna dare 777 a tutta la cartella ferroviaDrone
    if os.path.isfile('{}/tmp/output3d.zip'.format(outdir0)):       
        os.remove('{}/tmp/output3d.zip'.format(outdir0))

    try:
        # Connect to an existing database
        #conn = psycopg2.connect(host="192.168.2.28", port="5432", dbname="city_routing", user="postgres", password="postgresnpwd", options="-c search_path=network")
        con = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        print("connected!")
    except:
        print("unable to connect")
    
    # Open a cursor to perform database operations
    cur = con.cursor()
    
    query = """
        DROP TABLE IF EXISTS output2 ;
        DROP TABLE IF EXISTS output ;
        DROP INDEX IF EXISTS network_source_idx;
        DROP INDEX IF EXISTS network_target_idx;
        DROP TABLE IF EXISTS lines_split;
        DROP TABLE IF EXISTS points_snapped;
        DROP TABLE IF EXISTS ways_densified;
        DROP TABLE IF EXISTS points_over_lines;
        DROP TABLE IF EXISTS input_points;

        CREATE TABLE input_points (id SERIAL PRIMARY KEY);
        SELECT AddGeometryColumn('', 'input_points', 'geom', 4326, 'POINT', 2);
        CREATE INDEX input_points_geom_idx ON input_points USING gist (geom);

        INSERT INTO input_points( geom)
        VALUES (ST_PointFromText('POINT(%s %s)',4326));
        INSERT INTO input_points( geom)
        VALUES( ST_PointFromText('POINT(%s %s)',4326)); 

        CREATE TABLE points_over_lines
        AS SELECT a.id,ST_ClosestPoint(ST_Union(b.the_geom), a.geom)::geometry(POINT,4326) AS geom
        FROM input_points a, network.ways b
        GROUP BY a.geom,a.id;

        CREATE OR REPLACE FUNCTION ST_AsMultiPoint(geometry) RETURNS geometry AS
        'SELECT ST_Union((d).geom) FROM ST_DumpPoints($1) AS d;'
        LANGUAGE sql IMMUTABLE STRICT COST 10;

        CREATE TABLE ways_densified AS
        SELECT 1 AS id, ST_Union(ST_AsMultiPoint(st_segmentize(the_geom,0.00001)))::geometry(MULTIPOINT,4326) AS geom 
        FROM network.ways;

        CREATE TABLE points_snapped AS
        SELECT b.id, ST_snap(ST_Union(b.geom),a.geom, 0.000001)::geometry(POINT,4326) AS geom 
        FROM ways_densified a, points_over_lines b
        GROUP BY a.geom, b.geom, b.id;


        CREATE TABLE lines_split AS
        SELECT a.osm_id, (ST_Dump(ST_split(st_segmentize(a.the_geom,0.00001),ST_Union(b.geom)))).geom::geometry(LINESTRING,4326) AS geom 
        FROM network.ways a, points_snapped b
        GROUP BY a.osm_id, a.the_geom;

        ALTER TABLE lines_split ADD COLUMN idk serial PRIMARY KEY;
        ALTER TABLE lines_split ADD COLUMN source integer;
        ALTER TABLE lines_split ADD COLUMN target integer;

        SELECT pgr_createTopology('lines_split', 0.000001, 'geom', 'idk');

        CREATE INDEX network_source_idx ON lines_split("source");
        CREATE INDEX network_target_idx ON lines_split("target");

        ALTER TABLE lines_split ADD COLUMN cost numeric;
        UPDATE lines_split set cost = ST_Length(geom);

        ALTER TABLE points_snapped add column idk integer;

        UPDATE points_snapped p
        SET idk = v.id
        FROM lines_split_vertices_pgr v
        WHERE ST_Contains( v.the_geom, p.geom );

        CREATE TABLE output AS
        SELECT a.seq, a.node, a.edge, a.cost, b.geom
        FROM pgr_dijkstra('SELECT idk as id, source, target, cost FROM lines_split',
                         (SELECT idk FROM points_snapped p WHERE p.id = 1),
                         (SELECT idk FROM points_snapped p WHERE p.id = 2),
                          false) AS a  
        INNER JOIN lines_split b ON (a.edge = b.idk) ORDER BY seq;

        CREATE TABLE output2 AS
        SELECT a.seq, a.node, a.edge, a.cost, b.geom
        FROM pgr_dijkstra('SELECT idk as id, source, target, cost FROM lines_split',
                         (SELECT idk FROM points_snapped p WHERE p.id = 2),
                         (SELECT idk FROM points_snapped p WHERE p.id = 1),
                          false) AS a  
        INNER JOIN lines_split b ON (a.edge = b.idk) ORDER BY seq;		
    """
    
    #cur.execute(query, (8.944864369323, 44.42086708903617, 8.941936154051062, 44.42486689510227))
    cur.execute(query, (float(lon1), float(lat1), float(lon2), float(lat2)))
    con.commit()
    cur.close()
    con.close()
    
    #exit()
    comando_ogr='/usr/bin/ogr2ogr -f GPKG ./tmp/output.gpkg PG:"host={} port={} dbname={} user={} password={}" -sql "SELECT * from public.output" -overwrite'.format(host, port, dbname, user, password)
    #print(comando_ogr)
    os.system(comando_ogr)
    #exit()
    
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
    # startcmd = [grass7bin, '--config', 'path']
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
    # print(gisbase)
    
    
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
    
    print("init" in dir(grass.script.setup))
    print(gisbase)
    print(gisdb)
    #print(location)
    print(mapset)
    print(mapset)
    print('ok')

    # launch session
    rcfile = gsetup.init(gisbase, gisdb, location, mapset)
    
    print('session ok')

    # example calls
    #gscript.message('Current GRASS GIS 7 environment:')
    print (gscript.gisenv())
    
    #import data from postgresDB --> sql query result
    line2d = 'line2d'
    dem = 'dem_20'
    
    #set computational region to dem
    gscript.run_command('g.region', raster=dem, flags='ap')
    
    gscript.run_command('v.in.ogr', input='{}/tmp/output.gpkg'.format(outdir0), layer='sql_statement', output=line2d, type='line', overwrite=True)
    
    gscript.run_command('v.drape', input=line2d, type='line', output=tmp["line3d"], elevation=dem, method='bilinear')
    
    if ffile == 'csv':
        gscript.run_command('v.to.points', input=tmp["line3d"], type='line', output=tmp["point3d"], use='vertex')
        gscript.run_command('v.out.ascii', input=tmp["point3d"], type='point', output='{}/output3d.csv'.format(outdir), format='point', separator='comma', flags='c', overwrite=True)
    elif ffile == 'kml':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.kml'.format(outdir) , format='KML', overwrite=True)
    elif ffile == 'gml':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.gml'.format(outdir), format='GML', overwrite=True)
    elif ffile == 'geojson':
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.geojson'.format(outdir), format='GeoJSON', overwrite=True)
    else:
        gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.shp'.format(outdir), format='ESRI_Shapefile', overwrite=True)
        
    with ZipFile('{}/tmp/output3d.zip'.format(outdir0), 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(outdir):
           for filename in filenames:
               #create complete filepath of file in directory
               filePath = os.path.join(folderName, filename)
               # Add file to zip
               zipObj.write(filePath, basename(filePath))
        
    os.remove('{}/tmp/output.gpkg'.format(outdir0))
    gscript.run_command("g.remove", flags="f", type='raster,vector', name=",".join([tmp[m] for m in tmp.keys()]), quiet=True)
    

if __name__ == "__main__":
	main()
