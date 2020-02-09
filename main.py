import utils
from config import Bbox_1, Bbox_2

if __name__ == '__main__':
    downloaded_file_path = 'example/map.osm'

    # download a map file
    utils.download_map_file(Bbox_1, Bbox_2, path=downloaded_file_path)

    # output nodes
    node_cors = utils.node2dat(source=downloaded_file_path,
                               output_nodes='example/highway_output_nodes.dat')
    # output the graph
    node_details = utils.link2dat(node_cors=node_cors, source='example/map.osm',
                                  output_links='example/highway_output_links.dat',
                                  output_map='example/highway_map.png',
                                  exclude_unclassfied_point=True)
