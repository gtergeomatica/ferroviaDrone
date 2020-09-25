#!/usr/bin/env python
# coding=utf-8

import psycopg2
import os

def main():
    try:
        # Connect to an existing database
        #conn = psycopg2.connect(host="192.168.2.28", port="5432", dbname="city_routing", user="postgres", password="postgresnpwd", options="-c search_path=network")
        conn = psycopg2.connect(host="192.168.2.28", port="5432", dbname="city_routing", user="postgres", password="postgresnpwd")
        print("connected!")
    except:
        print("unable to connect")
    
    # Open a cursor to perform database operations
    cur = conn.cursor()
    
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
    
    cur.execute(query, (8.944864369323, 44.42086708903617, 8.941936154051062, 44.42486689510227))
    conn.commit()
    cur.close()
    conn.close()
    
    os.system('ogr2ogr   -f GPKG ./ferroviaDrone/output.gpkg PG:"host=192.168.2.28 port=5432 dbname=city_routing user=postgres password=postgresnpwd" -sql "SELECT * from public.output"')

if __name__ == "__main__":
	main()