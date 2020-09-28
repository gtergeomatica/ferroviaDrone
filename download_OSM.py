import requests
import json
import os

#definizione file di output
outdir = os.path.dirname(os.path.realpath(__file__))
osm_file = os.path.join(outdir,'data.osm')

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

response = requests.get(overpass_url, 
                        params={'data': overpass_query})
data = response.text

#scrive il risultato della query su un file data.osm
with open(osm_file, "w") as file:
    file.write(data)
file.close()

print('end')