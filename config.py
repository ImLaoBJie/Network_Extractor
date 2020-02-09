# Details of keys and values can be found in this website：
# https://wiki.openstreetmap.org/wiki/Key:highway
Exclusion = {'highway': ['residential', 'unclassified',
                         'living_street', 'service',
                         'pedestrian', 'track',
                         'bus_guideway', 'escape',
                         'raceway', 'road',  # unknown road
                         'footway', 'bridleway',
                         'steps', 'corridor',
                         'path', 'cycleway',
                         'proposed', 'construction',
                         'elevator', 'emergency_access_point',
                         'milestone', 'platform',
                         'rest_area', 'speed_camera',
                         'street_lamp', 'services',
                         'trailhead']
             }

'''
# The main road network
Exclusion = {'highway': ['residential',
                         'living_street', 'service',
                         'pedestrian', 'track',
                         'bus_guideway', 'escape',
                         'raceway', 'road',  # unknown road
                         'footway', 'bridleway',
                         'steps', 'corridor',
                         'path', 'cycleway',
                         'proposed', 'construction',
                         'elevator', 'emergency_access_point',
                         'milestone', 'platform',
                         'rest_area', 'speed_camera',
                         'street_lamp', 'services',
                         'trailhead']
             }
'''

'''
# The cycleway network
Exclusion = {'highway': ['motorway', 'trunk',
                         'motorway_link', 'trunk_link',
                         'bus_guideway', 'escape', 'raceway',
                         'steps',
                         'construction',
                         'elevator', 'platform'
                         ],
             'sidewalk': ['None'],
             'cycleway': ['None'],
             'bicycle_road': ['None'],
             'service': ['None'],
             }
'''
# (lat, lon) in the data

# bbox
# lon, lat 经度， 纬度

# Beijing, China
Bbox_1 = [116.16, 39.74]
Bbox_2 = [116.65, 40.10]

Access = list(Exclusion.keys())

Encoding = 'UTF-8'

