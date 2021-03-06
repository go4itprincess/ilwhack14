from twfy import TWFY
import json
import urllib2
import re

twfy = TWFY.TWFY('B7Ben2G9Zu2kCnRUEwFzJLea')

url = "http://mapit.mysociety.org/areas/SPC"
req = urllib2.Request(url)
constituencies_string = urllib2.urlopen(req).read()

constituencies = json.loads(constituencies_string, 'iso-8859-1')

output = []


for constituency in constituencies.values():
    id = constituency['id']
    name = constituency['name']

    url = "http://mapit.mysociety.org/area/" + str(id) + ".kml"
    req = urllib2.Request(url)

    polygons_scraped = re.findall("<coordinates>(.+?)</coordinates>",urllib2.urlopen(req).read())

    polygons = []

    for poly in polygons_scraped:
        coordinates = poly.split(' ')

        polygon = []
        i = 0

        for coordinate in coordinates:
            coordinate = map(float,coordinate.split(',')[:2])
            coordinate[0], coordinate[1] = coordinate[1], coordinate[0]

            if i%10 == 0:
                polygon.append(coordinate)
            i += 1

        polygons.append([polygon])

    output.append({"name":name,"id":id,"polygon":polygons})
    print name

fo = open("../testapp/static/polygons_clean_floats.js", "w+")
fo.write(json.dumps(output))
fo.close()

print "Done!"
