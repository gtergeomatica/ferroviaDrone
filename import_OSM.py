import requests
import json
import os
from conn import *
import logging
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='log/download_OSM.log',   #mancano permessi
    level=logging.INFO)

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)
osm_file = '/home/ubuntu/ferroviaDrone/data.osm'
logging.info('osm 2 pgrouting')
#Import in Postgres del file data.osm
p = """osm2pgrouting -f {0} -h {1} -U {2} -d {3} -p {4} -W {5}  --schema {6} --conf={7}""".format(osm_file,
                                                                                                  host,
                                                                                                  user,
                                                                                                  dbname,
                                                                                                  port,
                                                                                                  password,
                                                                                                  schema,
                                                                                                  conf)
 #"""osm2pgrouting -f data.osm -h localhost -U postgres -d city_routing -p 5432 -W postgresnpwd  --schema network --conf=/usr/share/osm2pgrouting/mapconfig_rail.xml"""

  
os.system(p)


logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 