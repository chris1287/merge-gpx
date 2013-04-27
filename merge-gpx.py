#!/usr/bin/python 

import xml.etree.ElementTree as ET
import sys
from math import radians, cos, sin, asin, sqrt
from datetime import datetime

def haversine(lon1, lat1, lon2, lat2):
	"""
	Calculate the great circle distance between two points 
	on the earth (specified in decimal degrees)
	http://stackoverflow.com/questions/4913349/haversine-formula-in-python-bearing-and-distance-between-two-gps-points
	"""
# convert decimal degrees to radians 
	lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
# haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
	c = 2 * asin(sqrt(a)) 
	km = 6367 * c
	return km 

def haversineGpx(point1, point2):
  lat1 = float(point1.attrib['lat'])
  lon1 = float(point1.attrib['lon'])
  lat2 = float(point2.attrib['lat'])
  lon2 = float(point2.attrib['lon'])
  return haversine(lon1, lat1, lon2, lat2)

def GpxToTime(point):
  timeElement = point.find('{0}time'.format(namespace))
  return datetime.strptime(timeElement.text, '%Y-%m-%dT%H:%M:%SZ')

def TimeToGpx(time):
  return time.strftime('%Y-%m-%dT%H:%M:%SZ')

file1 = sys.argv[1]
file2 = sys.argv[2]
file3 = sys.argv[3]

tree1 = ET.parse(file1)
tree2 = ET.parse(file2)
# namespace="{http://www.topografix.com/GPX/1/1}"
register_namespace('http://www.topografix.com/GPX/1/1')

trkpts1 = tree1.findall('*//{0}trkpt'.format(namespace))
trkpts2 = tree2.findall('*//{0}trkpt'.format(namespace))

# Get last point from 1
lastPoint = trkpts1[-1]

# Search closest point from 2
minimumPoint = trkpts2[0]
minimumDistance = haversineGpx(minimumPoint, lastPoint)
minimumIndex = 0
index = 0
for trkpt in trkpts2[1:]:
  index = index + 1
  distance = haversineGpx(trkpt, lastPoint)
  if distance < minimumDistance:
    minimumDistance = distance
    minimumPoint = trkpt
    minimumIndex = index

print 'The closest point is', minimumPoint.attrib['lat'], minimumPoint.attrib['lon'], minimumDistance, minimumIndex

# Get trkseg from 1
trkseg = tree1.find('*//{0}trkseg'.format(namespace))

# Change datetime from closest point 1 on and append updated point to tree1
timeLastPoint = GpxToTime(lastPoint)
timeClosestPoint = GpxToTime(minimumPoint)
timeDiff = timeLastPoint - timeClosestPoint
print 'The time difference is', timeDiff
for trkpt in trkpts2[minimumIndex:]:
  actualTime = GpxToTime(trkpt)
  actualTimeText = TimeToGpx(actualTime + timeDiff)
  trkpt.find('{0}time'.format(namespace)).text = actualTimeText
  trkseg.append(trkpt)

# Save updated tree1
tree1.write(file3)

