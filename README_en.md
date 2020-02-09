

# Network_Extractor
 Download and extract specific elements from OSM to form a network

---
# Before running it
1. Change the parameters of the functions
- `download_map_file`：
  - `Bbox_1`，`Bbox_2` refer to the range of the whole network;
  - `path` refers to the path and the name of the raw map file downloaded from the OSM;
  - If you have downloaded the raw map file, you can skip the execution of this function.

- `node2dat`：
  - `source` refers to the path and name of the raw map file mentioned above;
  - `output_nodes` refers to the output folder and name of the file storing all details of nodes within the range;
  - `return` this function will return a variable strong the details of nodes.

- `node_details`：
  - `node_cors` read the information from the variable created by `node2dat`;
  - `source` see the `source` in the function `node2dat`;
  - `output_links` refers to the output folder and name of the files saving the whole directed grapg;
  - `output_map` refers to the output folder and name of the rough diagram of the network.
  - `exclude_unclassfied_point`(type: bool) whether or not to exclude the nodes without tags，there are a few nodes marked as 'unclassified', if True, these points will not be saved in the file.

These parameters can be modified in 'main.py':
```
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
```

2. The description of the functions
 - `download_map_file` is used to download the raw map file from the OSM，The API used here is [Overpass API](https://overpass-api.de/api/map?bbox=). [Open Database License (ODbL) v1.0](https://opendatacommons.org/licenses/odbl/1.0/) must be followed.
 - `node2dat` is used to extract all details of nodes within the specific range，the ids of nodes will be sorted in the ascending order，the example can be found in `example/highway_output_nodes.dat`. The following contents are the detailed info of the output file，There are id，latitude，longitude from the left to the right side, separated by commas. This output file does not contain headers，you can add the header and change the type of the file to tranform it to the CSV file.
 
```
25248662,39.9062170,116.3912757
25248785,39.9062721,116.3894407
25248786,39.9063940,116.3930703
25248787,39.9065222,116.3970962
25248788,39.9016044,116.3896480
25248790,39.8987502,116.3898158
25248791,39.8988716,116.3934609
25585055,39.9019869,116.3855782
25585061,39.9016947,116.3862835
25585063,39.9014882,116.3867186
25585067,39.9017740,116.3854246
```
 
 - `node_details` will select the nodes satisfied the requirements and the related info od edges, the ids of nodes are sorted in the ascending order，the example can be founded in`example/highway_output_links.dat`. The following contents are the detailed info of the output files. From the left side to the right side，there are id，latitude，longitude, adjacently connected node's id(node_0)，distance(dist_0)，adjacently connected node's id(node_1)，distance(dist_1)......
 
```
25585116,39.9005436,116.3778503,339290761,45.15116728717983,5077274184,98.02485049470219
25585118,39.9022187,116.3777893,342803972,45.68438153945782,25585120,30.813435041475373
25585120,39.9024955,116.377788,25585118,30.813435041475373,25585122,49.470842030870934
25585122,39.9029395,116.3777633,25585120,49.470842030870934,533648145,68.41284263615997,5115805573,49.552443548807574
25585132,39.9029476,116.3816758,25585135,57.983657710893496,25585155,67.23514811948993
25585135,39.9024289,116.3816138,25585139,22.70246815167011,25585132,57.983657710893496
25585139,39.9022258,116.3815897,6795074474,40.8139009571648,25585135,22.70246815167011
```

The data will be saved in the form of directed graph. For example, the Node 0 and Node 1, are connected by a two-way road, and the distance between them is 100. This simple graph will be presented in the following form:

```
0, lat_0, lon_0, 1, 100
1, lat_1, lon_1, 0, 100
```

The operation of tranforming the output file to the CSV file is the sanme as that above.

3. Modify `config.py`
- `Exclusion` (type: dict)：
  A Dictionary，The keys of it is the main tags/labels illustrating the kinds of roads need to be selected，the corresponding lists are the minor tags/labels illustrating the roads need to be excluded from the above roads had been selected. For example, when the `Exclusion` have the following value:
  ```
  Exclusion = {'highway': ['secondary_link', 'tertiary_link']
               }
  ```
  Equivalent to：
  
  The roads need to be selected（Major tags/labels） | The roads need to be further excluded（Minor tags/labels）
  ------------ | -------------
  highway | secondary_link, tertiary_link
  
  In this case, all the roads with tag `highway` will be selected, but the roads with both tag `highway` and tag `secondary_link`/`tertiary_link` will be deleted.
  
  More details and description of details can be found in here：[Key:highway](https://wiki.openstreetmap.org/wiki/Key:highway?uselang=zh-CN)
  
 The notes in `config.py` provide the two examples of the variable `Exclusion` (i.e. the typical highway network and the cycleway network seperately)
  
- `Bbox_1`, `Bbox_2` (type: list)：
  List，The form of them is `Bbox_1 = [lon_0, lat_0]`，`Bbox_2 = [lon_1, lat_1]`，`Bbox_1` is the lower left corner of the range，`Bbox_2`is the upper right of that.Try to satisfy `lat_0<lat_1` and `lon_0<lon_1`, otherwise, the unknown errors may occur. Also, you can tranfer them directly to the parameters `Bbox_1`, `Bbox_2` in the function `download_map_file`, the effect is the same.
  
  The original value of this 2 variables in `config.py` is the urban and suburban area of the Beijing, China.
  
4. Notice：
 - The OSM add random changes when implement OSM projects within China to avoid ilegal issues. If you need to extract the info related to China, please be careful;
 - The coordinate system used by OSM is WGS-48;
 - Sometiems the OSM will not provide the distance between 2 nodes, the distance betwwen any 2 nodes will be calculated instead of using the values proveded by OSM, even though the values are not NAN values. The approch to realize this is to calculate the distance between 2 points on the surface of the sphere. The radius of EARTH is 6378.137km.
 
 # Start
 ```
 python main.py
 ```
 
 # Efficiency
 Apart from the uncertain time consumption on downloading the raw map file from OSM (it depends on your Internet Environment), the processing and extraction of a 40KM x 40KM map would be completed within 10 mins (when CPU is i7-9750H, generate the typical highway network mentioned in the example in `config.py` only consume 20 seconds), so the multiprocessing and parallelism are temporarily not considered. The raw map file  used in the demo can be downloaded from here (as an another source):[password:i4fh](https://pan.baidu.com/s/1y1iw_Ry7ZL-uQPz6C4p7wg)
 
 - [ ] TODO:multiprocessing
 
 # Result
 
 ![HighwayNetwork](https://github.com/ImLaoBJie/Network_Extractor/blob/master/example/highway_map.png)
 

 Enjoy it!:yum:
