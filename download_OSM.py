import requests
import json
import os
#from conn import *
import logging
logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    #filename='log/download_OSM.log',   #mancano permessi
    level=logging.INFO)

logging.info('*'*20 + ' NUOVA ESECUZIONE ' + '*'*20)


#definizione file di output
outdir = os.path.dirname(os.path.realpath(__file__))
osm_file = os.path.join(outdir,'data_it.osm')
logging.info(osm_file)

#query sul database OSM estrae tag railway con valore rail, narrow_gauge e preserved per tutta Italia
overpass_url = "http://overpass-api.de/api/interpreter"
overpass_query = """
[timeout:900][maxsize:1073741824][out:xml];
(node["railway"="rail"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 way["railway"="rail"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 rel["railway"="rail"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 node["railway"="narrow_gauge"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 way["railway"="narrow_gauge"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 rel["railway"="narrow_gauge"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 node["railway"="preserved"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 way["railway"="preserved"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
 rel["railway"="preserved"](35.1423311340000026,6.4726878990000003,47.5951051549999988,20.2665936329999994);
);
(._;>;);
out meta;
"""
logging.info('Lancio query')
response = requests.get(overpass_url, 
                        params={'data': overpass_query})
                        
if response.ok:
    logging.info('Query eseguita con successo!')
else:
    logging.error('Query fallita!')
    logging.error(response)
    os._exit(1)

                        
logging.info('Recupero dati')
try:                      
    data = response.text
except:
    logging.error('Recupero dati fallito')
    os._exit(1)

    
#scrive il risultato della query su un file data.osm
logging.info('Scrivo file .osm')
with open(osm_file, "w") as file:
    file.write(data)
file.close()
'''
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
'''


logging.info('*'*20 + ' ESCO NORMALMENTE' + '*'*20) 