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
import logging

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='log/path3d.log',   #mancano permessi
    level=logging.DEBUG)

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)

def main():

    script, lon1, lat1, lon2, lat2, ffile = argv
    logging.debug('sono in def')
    logging.debug('START = lon1 {0}, lat1 {1}'.format(lon1, lat1))
    logging.debug('STOP = lon2 {0}, lat2 {1})'.format(lon2, lat2))
    
    
    # Define output directories
    outdir0 = os.path.dirname(os.path.realpath(__file__))
    outdir='{}/output3d'.format(outdir0)
    
    # Remove existing file in outdir
    for path in os.listdir(outdir):
        full_path = os.path.join(outdir, path)
        if os.path.isfile(full_path):
            os.remove(full_path)
    # Remove previously created zip file
    if os.path.isfile('{}/tmp/output3d.zip'.format(outdir0)):       
        os.remove('{}/tmp/output3d.zip'.format(outdir0))

    try:
        # Connect to an existing database
        con = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)
        logging.info("connected!")
    except psycopg2.Error as e:
        logging.error("unable to connect")
        logging.error(e.pgerror)
        os._exit(1)
   
    # Open a cursor to perform database operations
    cur = con.cursor()
    
    # First DB query
    logging.info('Import input points')
    query1 = """
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
        """
    try:
        # Execute the first query passing arguments
        cur.execute(query1, (float(lon1), float(lat1), float(lon2), float(lat2)))
        con.commit()
    except psycopg2.Error as e:
        logging.error('Query 1 failed- Unable to import input points')
        logging.error(e.pgerror)
        os._exit(1)

    # Second DB query 
    logging.info('Query 2')
    query2 = """
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
        """
    try:
        # Execute the second query
        cur.execute(query2)
        con.commit()
    except psycopg2.Error as e:
        logging.error('Query 2 failed!: Unable to snap points to ways')
        logging.error(e.pgerror)
        os._exit(1)

    # Third DB query  
    logging.info('Query 3')
    query3 = """

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

        --UPDATE points_snapped p
        --SET idk = v.id
        --FROM lines_split_vertices_pgr v
        --WHERE ST_Contains( v.the_geom, p.geom );
        
        UPDATE points_snapped p
        SET idk = (
            SELECT id 
            FROM lines_split_vertices_pgr v
            ORDER BY p.geom <-> v.the_geom LIMIT 1);

        CREATE TABLE output AS
        SELECT a.seq, a.node, a.edge, a.cost, b.geom
        FROM pgr_dijkstra('SELECT idk as id, source, target, cost FROM lines_split',
                         (SELECT idk FROM points_snapped p WHERE p.id = 1),
                         (SELECT idk FROM points_snapped p WHERE p.id = 2),
                          false) AS a  
        INNER JOIN lines_split b ON (a.edge = b.idk) ORDER BY seq;
	
    """
    try:
        # Execute the third query
        cur.execute(query3)
        con.commit()
    except psycopg2.Error as e:
        logging.error('Query3 failed! - unable to find route')
        logging.error(e.pgerror)
        os._exit(1)
    
    # Check if the output DB table is empty
    if cur.rowcount == 0:
        logging.error('Empty output table')
        os._exit(1)
    else:
       logging.info('numero di rige in output {}'.format(cur.rowcount))
    # Close cursor and DB connection
    cur.close()
    con.close()
    logging.info('Connection closed!')
    
    # Save DB output table as geopackage (due to bug in grass connection to DB Postgis )
    logging.info('Ogr2ogr conversion')
    comando_ogr='/usr/bin/ogr2ogr -f GPKG {}/tmp/output.gpkg PG:"host={} port={} dbname={} user={} password={}" -sql "SELECT * from public.output" -overwrite'.format(outdir0, host, port, dbname, user, password)
    os.system(comando_ogr)
    
    # Define temporary maps name
    global tmp
    tmp = {}
    processid = "{:.2f}".format(time.time())
    processid = processid.replace(".", "_")
    tmp["line3d"] = "line3d_" + processid
    tmp["point3d"] = "point3d_" + processid
    
    # Define GRASS Database
    gisdb = os.path.join(os.path.expanduser("~"), "/home/ubuntu/grass_DB")

    # Specify (existing) Location and Mapset
    location = "wgs84"
    mapset = "ferroviadrone"

    # Define path to the GRASS GIS launch script
    grass7bin = 'grass78'
    # query GRASS GIS itself for its GISBASE (not used since it doesn't work from php)
    # startcmd = [grass7bin, '--config', 'path']
    # p = subprocess.Popen(startcmd, shell=False,
                         # stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = p.communicate()
    # if p.returncode != 0:
        # print >>sys.stderr, "ERROR: Cannot find GRASS GIS 7 start script (%s)" % startcmd
        # sys.exit(-1)
    # gisbase = out.strip(b'\n\r')
    # gisbase = str(gisbase, 'utf-8')
      
    # Set GISBASE environment variable
    gisbase = '/usr/local/grass78'
    os.environ['GISBASE'] = gisbase
    
    #os.environ['PATH'] += os.pathsep + os.path.join(gisbase, 'extrabin')
    # Add path to GRASS addons (not needed in this case)
    #home = os.path.expanduser("~")
    #os.environ['PATH'] += os.pathsep + os.path.join(home, '.grass7', 'addons', 'scripts')
    
    # Set HOME environment variable (required to launch the python script from web --> php server does not find home location)
    home = '/home/ubuntu/'
    os.environ['HOME'] = home

    # Define GRASS-Python environment
    grass_pydir = os.path.join(gisbase, "etc", "python")
    sys.path.append(grass_pydir)
    
    # import (some) GRASS Python bindings
    import grass.script as gscript
    import grass.script.setup as gsetup

    # Launch grass session
    rcfile = gsetup.init(gisbase, gisdb, location, mapset)
    
    # Define main input and output map
    line2d = 'line2d'
    dem = 'dem20'
    
    # Set computational region to dem map
    gscript.run_command('g.region', raster=dem, flags='ap')
    
    # Import the geopackage resulting from the DB query
    gscript.run_command('v.in.ogr', input='{}/tmp/output.gpkg'.format(outdir0), layer='sql_statement', output=line2d, type='line', overwrite=True)
    
    # Convert 2D geometrie to 3D
    gscript.run_command('v.drape', input=line2d, type='line', output=tmp["line3d"], elevation=dem, method='bilinear')
    
    # Export the 3D feature depending on required format
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
    
    # Create a zip file with the final output
    with ZipFile('{}/tmp/output3d.zip'.format(outdir0), 'w') as zipObj:
        # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(outdir):
           for filename in filenames:
               # Create complete filepath of file in directory
               filePath = os.path.join(folderName, filename)
               # Add file to zip
               zipObj.write(filePath, basename(filePath))
               
    # Remove unuseful file like the geopackage adn the tmp file from the grass mapset    
    os.remove('{}/tmp/output.gpkg'.format(outdir0))
    gscript.run_command("g.remove", flags="f", type='raster,vector', name=",".join([tmp[m] for m in tmp.keys()]), quiet=True)
    

if __name__ == "__main__":
	main()

logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 
