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
    filename='log/path3d.log',
    level=logging.INFO)

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


    # Connect to an existing database
    try:
        
        con = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password, **keepalive_kwargs)
        logging.info("connected!")
    except psycopg2.Error as e:
        logging.error("unable to connect")
        logging.error(e.pgerror)
        os._exit(1)
   
    # Open a cursor to perform database operations
    cur = con.cursor()
    
    # First DB query
    logging.info('Query 1 - Importing input points')
    query1 = """
        -- Clean schema
        DROP TABLE IF EXISTS output2 ;
        DROP TABLE IF EXISTS output ;
        DROP INDEX IF EXISTS network_source_idx;
        DROP INDEX IF EXISTS network_target_idx;
        DROP TABLE IF EXISTS lines_split;
        DROP TABLE IF EXISTS points_snapped;
        DROP TABLE IF EXISTS ways_densified;
        DROP VIEW IF EXISTS ways_subset;
        DROP TABLE IF EXISTS points_over_lines;
        DROP TABLE IF EXISTS input_points;
        
        -- Define input geometry
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
    logging.info('Query 2 - Snapping points to ways')
    query2 = """
        -- Subset network  
        CREATE VIEW ways_subset AS
        SELECT *
        FROM ways a, (SELECT St_buffer(ST_Collect(geom), 0.2) as geom FROM input_points) b
        WHERE a.the_geom && b.geom;    
        
        -- Find closest points
        CREATE TABLE points_over_lines
        AS SELECT a.id,ST_ClosestPoint(ST_Union(b.the_geom), a.geom)::geometry(POINT,4326) AS geom
        FROM input_points a, ways_subset b
        GROUP BY a.geom,a.id;

        -- Densify network 
        CREATE OR REPLACE FUNCTION ST_AsMultiPoint(geometry) RETURNS geometry AS
        'SELECT ST_Union((d).geom) FROM ST_DumpPoints($1) AS d;'
        LANGUAGE sql IMMUTABLE STRICT COST 10;

        CREATE TABLE ways_densified AS
        SELECT 1 AS id, ST_Union(ST_AsMultiPoint(st_segmentize(the_geom,0.00001)))::geometry(MULTIPOINT,4326) AS geom 
        FROM ways_subset;
        
        --Snap points to network
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
    logging.info('Query 3 - Finding shortest path')
    query3 = """

        -- Create network splitted on points snapped
        CREATE TABLE lines_split AS
        SELECT a.osm_id, (ST_Dump(ST_split(st_segmentize(a.the_geom,0.00001),ST_Union(b.geom)))).geom::geometry(LINESTRING,4326) AS geom 
        FROM ways_subset a, points_snapped b
        GROUP BY a.osm_id, a.the_geom;

        -- Recreate topology
        ALTER TABLE lines_split ADD COLUMN idk serial PRIMARY KEY;
        ALTER TABLE lines_split ADD COLUMN source integer;
        ALTER TABLE lines_split ADD COLUMN target integer;

        SELECT pgr_createTopology('lines_split', 0.000001, 'geom', 'idk');

        CREATE INDEX network_source_idx ON lines_split("source");
        CREATE INDEX network_target_idx ON lines_split("target");

        -- Defininf cost as length
        ALTER TABLE lines_split ADD COLUMN cost numeric;
        UPDATE lines_split set cost = ST_Length(geom);

        ALTER TABLE points_snapped add column idk integer;

        -- Find nearest vertex id to snapped points
        UPDATE points_snapped p
        SET idk = (
            SELECT id 
            FROM lines_split_vertices_pgr v
            ORDER BY p.geom <-> v.the_geom LIMIT 1);

        -- Find shortest path with pgr_dijkstra algorithm     
        CREATE OR REPLACE FUNCTION wrk_dijkstra(
            OUT seq INTEGER,
            OUT node BIGINT,
            OUT edge BIGINT,
            OUT cost DOUBLE PRECISION,
            OUT geom geometry)
            RETURNS SETOF record AS
            $BODY$
            WITH
            dijkstra AS (
            SELECT * FROM pgr_dijkstra(
                'SELECT idk AS id, * FROM lines_split',
                (SELECT idk FROM points_snapped p WHERE p.id = 1),
                (SELECT idk FROM points_snapped p WHERE p.id = 2),
                directed := false)
            ),
            get_geom AS (
            SELECT dijkstra.*,
                -- adjust directionality
                CASE
                    WHEN dijkstra.node = lines_split.source THEN geom
                    ELSE ST_Reverse(geom)
                END AS route_geom
            FROM dijkstra JOIN lines_split ON (edge = idk)
            ORDER BY seq)
            
            SELECT seq, node, edge, cost,    
               route_geom as geom
               FROM get_geom
               ORDER BY seq;
            $BODY$
            LANGUAGE 'sql';

        CREATE TABLE output AS
        SELECT * from wrk_dijkstra();

    """
    try:
        # Execute the third query
        cur.execute(query3)
        con.commit()
    except psycopg2.Error as e:
        logging.error('Query3 failed! - unable to find shortest path')
        logging.error(e.pgerror)
        os._exit(1)
    
    # Check if the output DB table is empty
    if cur.rowcount == 0:
        logging.error('Empty output table')
        os._exit(1)
    else:
       logging.debug('numero di rige in output {}'.format(cur.rowcount))
    # Close cursor and DB connection
    cur.close()
    con.close()
    logging.info('Connection closed!')
    
    # Save DB output table as geopackage (due to bug in grass connection to DB Postgis )
    logging.info('Ogr2ogr conversion')
    try:
        comando_ogr='/usr/bin/ogr2ogr -f GPKG {}/tmp/output.gpkg PG:"host={} port={} dbname={} user={} password={}" -sql "SELECT * from public.output" -overwrite'.format(outdir0, host, port, dbname, user, password)
        os.system(comando_ogr)
    except:
        logging.error('Unable to create the output.gpkg file')
        os._exit(1)
    
    # Define temporary maps name
    logging.info('Defining GRASS GIS environment')
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
    try:
        import grass.script as gscript
        import grass.script.setup as gsetup
        from grass.exceptions import CalledModuleError
    except ImportError as e:
        logging.error(e)
        os._exit(1)

    # Launch grass session
    logging.info('Launching GRASS GIS session')
    rcfile = gsetup.init(gisbase, gisdb, location, mapset)
    
    # Define main input and output map
    line2d = 'line2d'
    dem = 'dem20'
    
    # Set computational region to dem map
    logging.info('Setting computational region')
    gscript.run_command('g.region', raster=dem, flags='ap')
    
    # Import the geopackage resulting from the DB query
    logging.info('Importing the query result')
    if os.path.isfile('{}/tmp/output.gpkg'.format(outdir0)):
        try:
            gscript.run_command('v.in.ogr', input='{}/tmp/output.gpkg'.format(outdir0), layer='sql_statement', output=line2d, type='line', overwrite=True, quiet=True)
        except CalledModuleError as e1:
            logging.error(e1)
            os._exit(1)
    else:
        logging.error('The output.gpkg file does not exist')
        os._exit(1)
        
    
    # Convert 2D geometrie to 3D
    logging.info('Converting 2D features to 3D')
    try:
        gscript.run_command('v.drape', input=line2d, type='line', output=tmp["line3d"], elevation=dem, method='bilinear', quiet=True)
    except CalledModuleError as e2:
        logging.error(e2)
        os._exit(1)
    
    # Export the 3D feature depending on required format
    logging.info('Exporting results')
    try:
        if ffile == 'csv':
            gscript.run_command('v.to.points', input=tmp["line3d"], type='line', output=tmp["point3d"], use='vertex', quiet=True)
            gscript.run_command('v.out.ascii', input=tmp["point3d"], type='point', output='{}/output3d.csv'.format(outdir), format='point', separator='comma', flags='c', overwrite=True, quiet=True)
        elif ffile == 'kml':
            gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.kml'.format(outdir) , format='KML', overwrite=True, quiet=True)
        elif ffile == 'gml':
            gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.gml'.format(outdir), format='GML', overwrite=True, quiet=True)
        elif ffile == 'geojson':
            gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.geojson'.format(outdir), format='GeoJSON', overwrite=True, quiet=True)
        else:
            gscript.run_command('v.out.ogr', input=tmp["line3d"], output='{}/output3d.shp'.format(outdir), format='ESRI_Shapefile', overwrite=True, quiet=True)
    except CalledModuleError as e3:
        logging.error(e3)
        os._exit(1)
    
    # Create a zip file with the final output
    logging.info('Preparing the zip file for download')
    if os.path.exists(outdir) and os.path.isdir(outdir):
        if os.listdir(outdir):
            with ZipFile('{}/tmp/output3d.zip'.format(outdir0), 'w') as zipObj:
                # Iterate over all the files in directory
                for folderName, subfolders, filenames in os.walk(outdir):
                   for filename in filenames:
                       # Create complete filepath of file in directory
                       filePath = os.path.join(folderName, filename)
                       # Add file to zip
                       zipObj.write(filePath, basename(filePath))
        else:    
            logging.error('the {} directory is empty'.format(outdir))
            os._exit(1)
    else:
        logging.error('the {} directory does not exist'.format(outdir))
        os._exit(1)

               
    # Remove unuseful file like the geopackage adn the tmp file from the grass mapset
    logging.info('Removing temporary file')
    os.remove('{}/tmp/output.gpkg'.format(outdir0))
    gscript.run_command("g.remove", flags="f", type='raster,vector', name=",".join([tmp[m] for m in tmp.keys()]), quiet=True)
    

if __name__ == "__main__":
	main()

logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 
