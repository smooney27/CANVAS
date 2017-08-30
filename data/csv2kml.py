import sys
import os.path
import csv
from django.core.management import setup_environ
sys.path.append(os.path.join(os.path.dirname(__file__), '../streetview'))

readfile = open("./NationalSampleFinalSelected.csv", 'rU')
writefile = open("./NationalSampleFinalSelected.kml", 'w')
writefile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
writefile.write("<kml xmlns=\"http://www.opengis.net/kml/2.2\">\n")
writefile.write("<Document>\n")
writefile.write("<name>Streetview 150 Blocks Final</name>\n")
writefile.write("<description>The 150 blocks used for the Summer 2011 test of the Streetview street rating system.</description>\n")

try:
    reader = csv.reader(readfile, dialect='excel')
    for index, row in enumerate(reader):
        name = row[0] + ', ' + row[1]
        start_lng = float(row[3])
        start_lat = float(row[4])
        end_lng = float(row[5])
        end_lat = float(row[6])
        print "Found street segment in %s from (%f, %f)->(%f, %f)" % (name, start_lat, start_lng, end_lat, end_lng)
        kml_line = "<Placemark><name>%s</name><description>%s</description><Point><coordinates>%f,%f,0</coordinates></Point></Placemark>\n" % (name, name, start_lng, start_lat)
        writefile.write(kml_line)
    writefile.write("</Document>\n")
    writefile.write("</kml>\n")

finally:
    readfile.close()
    writefile.close()