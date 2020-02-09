from xml.etree.ElementTree import ElementTree, XMLParser
import requests
import math
import gc
import copy

import numpy as np

import matplotlib.pyplot as plt
import networkx as nx

from tqdm import tqdm

from config import Access, Exclusion, Bbox_1, Bbox_2, Encoding


def download_map_file(coordinate_1: list, coordinate_2: list, path='map.osm'):
    """Download the OSM data to the local directory.

        :param path: The downloaded file's name
        :param coordinate_1: The upper-left point of the selected bounding box.
        :param coordinate_2: The lower-right point of the selected bounding box.
        :return: None
    """
    # bbox: lat1,lon1,lat2,lon2
    bbox = [str(coordinate_1[0]), str(coordinate_1[1]), str(coordinate_2[0]), str(coordinate_2[1])]
    # use Overpass API
    bbox = ','.join(bbox)
    url = 'https://overpass-api.de/api/map?bbox=' + bbox

    headers = {'Proxy-Connection': 'keep-alive'}
    response = requests.request("GET", url, stream=True, data=None, headers=headers)
    file = open(path, 'wb')
    for chunk in tqdm(response.iter_content(chunk_size=1024), ascii=True, unit='kB', unit_scale=10, desc='Handling...'):
        if chunk:
            file.write(chunk)
            # file.flush()
    '''
    # Simple implementation
    r = requests.get(url)
    with open(name, 'wb') as file:
        file.write(r.content)
    '''

    print('\ndownloaded!')
    return True


class BinarySearch(object):
    """Binary Search Algorithm.

        This class is used to search target_id.

        *node_ids* is an required list which is storing
        the ids of nodes.

        """
    def __init__(self, node_ids: list):
        self.node_ids = node_ids
        self.length = len(node_ids)

    # return the index of the target_id
    def search(self, target_id: int):
        lower = 0
        upper = self.length - 1
        while lower <= upper:
            mid = int((lower + upper) / 2)
            if self.node_ids[mid] == target_id:
                return mid
            if self.node_ids[mid] > target_id:
                upper = mid - 1
            if self.node_ids[mid] < target_id:
                lower = mid + 1
        return -1


# Calculate Euclidean distance based on latitude and longitude coordinates
class CaculateDistance(object):
    """Calculate distances based on coordinates.

            This class is used to calculate Euclidean distance.

            *coordinate1* is an required list which stores the location of the first point
            *coordinate2* is an required list which stores the location of the second point

            """

    def __init__(self, coordinate1: list, coordinate2: list):
        self.EARTH_RADIUS = 6378.137
        self.lat1 = float(coordinate1[0])
        self.lng1 = float(coordinate1[1])
        self.lat2 = float(coordinate2[0])
        self.lng2 = float(coordinate2[1])

    def update(self, coordinate1: list, coordinate2: list):
        self.lat1 = float(coordinate1[0])
        self.lng1 = float(coordinate1[1])
        self.lat2 = float(coordinate2[0])
        self.lng2 = float(coordinate2[1])

    def rad(self, d):
        return d * math.pi / 180.0

    def getDistance(self):
        radLat1 = self.rad(self.lat1)
        radLat2 = self.rad(self.lat2)
        delta_radLat = radLat1 - radLat2
        delta_radLng = self.rad(self.lng1) - self.rad(self.lng2)
        s = 2 * math.asin(math.sqrt(
            math.pow(math.sin(delta_radLat / 2), 2) + math.cos(radLat1) * math.cos(radLat2) *
            math.pow(math.sin(delta_radLng / 2), 2)
        ))
        s = s * self.EARTH_RADIUS
        # meters
        s = (s * 10000) / 10
        return float(s)


def node2dat(source='map.osm', output_nodes='output_nodes.dat'):
    """Read details of nodes from the OSM file and write them to the raw files.
            :param source: The OSM file downloaded.
            :param output_nodes: The output raw file saving nodes info.
            :return: node_cors: The ids and relevant location of nodes
    """
    # IMPORTANCE: The ids of nodes have been sorted in ascending order.

    tree = ElementTree()
    parser = XMLParser(encoding=Encoding)
    tree.parse(source, parser=parser)
    # get parent
    root = tree.getroot()

    # open a new raw file
    file_1 = open(output_nodes, 'w')

    # the list storing id for search
    # WARNING: The list may occupy a large proportion of memory
    node_cors = {}

    # initialize all nodes
    extraction = ['id', 'lat', 'lon']
    for node in root.iter('node'):
        info = []
        for attrib in extraction:
            info.append(node.get(attrib))
        # not allow a node_id to have two (x,y) coordinates
        node_cors[(int(node.get('id')))] = [float(node.get('lat')), float(node.get('lon'))]
        file_1.write(','.join(info))
        file_1.write('\n')

    file_1.close()
    gc.collect()
    return node_cors


class TemporaryNode(object):
    """Store the node_id temporarily.

        This class is used to store the node_id temporarily.

        *first_node* is an required list which stores the first node_id

    """
    def __init__(self, first_node: int):
        self.current_node = first_node
        self.previous_node = 0

    def update(self, next_node: int):
        self.previous_node = self.current_node
        self.current_node = next_node

    def first(self):
        return int(self.previous_node)

    def second(self):
        return int(self.current_node)


def link2dat(node_cors: dict, source='map.osm', output_links='output_links.dat', output_map='map.jpg',
             exclude_unclassfied_point=False):
    """Read details of links from the OSM file and write them to the raw files.
            :param node_cors: The temporary dict saving node coordinates from the FUNCTION 'node2dat' (lat, lon).
            :param source: The OSM file downloaded.
            :param output_links: The output raw file saving links info.
            :param output_map: The image of overall network.
            :param exclude_unclassfied_point: Drop the unclassified points when True
            :return: node_details：The dict storing the neighbors and adjacencies.
    """
    # IMPORTANCE: The ids of ways have been sorted in ascending order.

    # write adjacency distances
    file_2 = open(output_links, 'w')

    # initialize the calculating object
    Distance = CaculateDistance([0.0, 0.0], [0.0, 0.0])

    # node_details storing the neighbors and adjacencies
    # may double the usage of memory
    node_details = copy.deepcopy(node_cors)

    tree = ElementTree()
    parser = XMLParser(encoding=Encoding)
    tree.parse(source, parser=parser)
    # get parent
    root = tree.getroot()

    num_null = 0
    num_links = 0
    num_unqualified = 0
    for way in root.iter('way'):
        tag_recorder = None

        num_links = num_links + 1
        # exclude the links that the bicycles cannot go through
        if way.find('tag') is None:
            # most of the links of Type-missed can be used bu bikes
            num_null = num_null + 1
            tag_isNull = True
            # continue
        else:
            tag_isNull = False
            for tag in way.iter('tag'):
                # just record the first qualified tag
                if tag.get('k') in Access:
                    tag_recorder = tag
                    break

        if tag_isNull:
            if exclude_unclassfied_point:
                continue
            else:
                pass
        elif tag_recorder is None:
            num_unqualified = num_unqualified + 1
            continue
        elif tag_recorder.get('v') in Exclusion[tag_recorder.get('k')]:
            num_unqualified = num_unqualified + 1
            continue
        else:
            pass

        counter = 0
        node_unit = None
        for node in way.iter('nd'):
            # ignore the first elements
            if counter == 0:
                counter = counter + 1
                node_unit = TemporaryNode(int(node.get('ref')))
                continue

            node_unit.update(int(node.get('ref')))
            Distance.update(node_cors[node_unit.first()], node_cors[node_unit.second()])
            # add distance and two-way link
            node_details[node_unit.first()].append([node_unit.second(), Distance.getDistance()])
            node_details[node_unit.second()].append([node_unit.first(), Distance.getDistance()])

    print('Type-missed links/Total num of links: {}/{}'.format(num_null, num_links))
    print('Acceptable links/Total num of links: {}/{}'.format(num_links - num_unqualified, num_links))

    # remove alone point
    num_del = 0
    num_nodes = 0
    element_to_del = []
    for node_id, contents in node_details.items():
        num_nodes = num_nodes + 1
        if len(contents) <= 2:
            element_to_del.append(node_id)
            num_del = num_del + 1
    for node_id in element_to_del:
        node_details.pop(node_id)
        node_cors.pop(node_id)
    print('Alone nodes/Total num of nodes: {}/{}'.format(num_del, num_nodes))

    # drawing the graph (with direction) of nodes and edges
    DiGraph = nx.DiGraph()
    DiGraph.add_nodes_from(list(node_cors.keys()))

    # write to file
    for node_id, contents in node_details.items():
        wait_to_write = [node_id, contents[0], contents[1]]
        # The details of adjacencies start at index 2
        for index in range(2, len(contents)):
            wait_to_write.append(contents[index][0])
            wait_to_write.append(contents[index][1])
            DiGraph.add_edge(node_id, contents[index][0], weight=contents[index][1])

        file_2.write(','.join(map(str, wait_to_write)))
        file_2.write('\n')

    file_2.close()

    # (lat, lon) -> (lon, lat)
    for key in node_cors.keys():
        i_cors = node_cors[key]
        node_cors[key] = [i_cors[1], i_cors[0]]

    # You can change the parameters of the plot here
    fig, ax = plt.subplots(1, 1, figsize=(25, 25))
    nx.draw_networkx_nodes(G=DiGraph, pos=node_cors, node_size=1, node_color='r', node_shape='.', ax=ax)
    nx.draw_networkx_edges(G=DiGraph, pos=node_cors, width=0.5, edge_color='b', arrows=False, ax=ax)

    lat_add = (Bbox_2[1] - Bbox_1[1]) / 100
    lon_add = (Bbox_2[0] - Bbox_1[0]) / 100
    ax.set_ylim(Bbox_1[1] - lat_add, Bbox_2[1] + lat_add)
    ax.set_xlim(Bbox_1[0] - lon_add, Bbox_2[0] + lon_add)
    ax.set_yticks(np.arange(Bbox_1[1], Bbox_2[1], 0.1))
    ax.set_xticks(np.arange(Bbox_1[0], Bbox_2[0], 0.1))
    ax.tick_params(
        size=5,
        labelsize=25,
        axis='both',
        which='both',
        bottom=True,
        left=True,
        labelbottom=True,
        labelleft=True)
    ax.set_ylabel('Latitude', fontdict={'size': 30})
    ax.set_xlabel('Longitude', fontdict={'size': 30})
    fig.savefig(output_map)

    return node_details
