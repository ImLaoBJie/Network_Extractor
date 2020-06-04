English Version: [README](https://github.com/ImLaoBJie/Network_Extractor/blob/master/README_en.md)


# Network_Extractor
 下载并提取特定路网节点

---
# 开始之前
1. 指定函数参数
- `download_map_file`：
  - `Bbox_1`，`Bbox_2`指定需要提取的路网范围；
  - `path`指定从OSM中下载未处理的原始地图文件的路径和文件名；
  - 若地图文件已经下载过可以直接注释掉。

- `node2dat`：
  - `source`指定刚才下载的原始地图文件路径和文件名；
  - `output_nodes`指定储存所有目标范围内的节点信息的文件路径和文件名；
  - `return`该函数会返回储存节点信息的变量。

- `node_details`：
  - `node_cors`读入`node2dat`函数返回的变量；
  - `source`同上，指定刚才下载的原始地图文件路径和文件名；
  - `output_links`指定储存有向图的文件路径和文件名；
  - `output_map`指定示意图的导出路径和文件名；
  - `exclude_unclassfied_point`(type: bool)是否排除没有指定类型的节点，OSM中存在少量unclassified的节点，如果为真，则排除这些节点，不存入文件。

在main.py中修改即可：
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

2. 函数说明
 - `download_map_file`函数用于从OSM中下载未处理的原始地图文件，使用的API为[Overpass API](https://overpass-api.de/api/map?bbox=)，遵守[开放数据共享开放数据库许可协议](https://opendatacommons.org/licenses/odbl/1.0/)。`path`参数指定路径与文件名。
 - `node2dat`函数提取并储存所有目标范围内的节点信息，节点id升序排列，示例文件位于仓库中的`example/highway_output_nodes.dat`。以下是文件的部分详细内容，从左到右分别为节点id，纬度latitude，经度longitude，并以逗号作为间隔。此文件为方便读取并未设置header，可自行在第一行写入header，并修改扩展名转换为csv文件。
 
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
 
 - `node_details`函数筛选符合的节点以及与之相连的其他节点,节点id升序排列，示例文件位于仓库中的`example/highway_output_links.dat`。以下是文件的部分详细内容，从左到右分别为节点id，纬度latitude，经度longitude，相连节点的id(node_0)，距离(dist_0)，相连节点的id(node_1)，距离(dist_1)......
 
```
25585116,39.9005436,116.3778503,339290761,45.15116728717983,5077274184,98.02485049470219
25585118,39.9022187,116.3777893,342803972,45.68438153945782,25585120,30.813435041475373
25585120,39.9024955,116.377788,25585118,30.813435041475373,25585122,49.470842030870934
25585122,39.9029395,116.3777633,25585120,49.470842030870934,533648145,68.41284263615997,5115805573,49.552443548807574
25585132,39.9029476,116.3816758,25585135,57.983657710893496,25585155,67.23514811948993
25585135,39.9024289,116.3816138,25585139,22.70246815167011,25585132,57.983657710893496
25585139,39.9022258,116.3815897,6795074474,40.8139009571648,25585135,22.70246815167011
```

数据以有向图形式保存，比如节点0和节点1以双向道路连接，距离为100m，则有：

```
0, lat_0, lon_0, 1, 100
1, lat_1, lon_1, 0, 100
```

如果需要读取该文件，建议采用以下方式：
```
def load_from_file(graph: str):
    file = open(graph, 'r')
    edges = {}
    coordinates = {}
    for adjacency in file.readlines():
        current_line = adjacency.split(',')
        node_id = int(current_line[0])
        iter_edges = {}
        for index in np.arange(3, len(current_line), 2):
           iter_edges[int(current_line[index])] = float(current_line[index + 1])

        edges[node_id] = iter_edges

        coordinate[node_id] = [float(current_line[1]), float(current_line[2])]
```

3. 修改config.py文件
- `Exclusion`变量(type: dict)：
  字典类型，字典键值keys()为需要提取的主要道路类型，键值对应内容为该主要道路类型中需要排除的次要道路类型，例如，当变量具有以下形式时：
  ```
  Exclusion = {'highway': ['secondary_link', 'tertiary_link']
               }
  ```
  等同于：
  
  需要读取的主要道路类型（一级标签） | 需要排除的次要道路类型（二级标签）
  ------------ | -------------
  highway | secondary_link, tertiary_link
  
  此时，所有公路highway都会被提取，但是highway中包含的二级道路和三级道路会被排除。
  
  详细的类型说明以及对应的标签名位于此处：[Key:highway](https://wiki.openstreetmap.org/wiki/Key:highway?uselang=zh-CN)
  
  config.py的注释中直接提供了两种路网类型的`Exclusion`变量示例，分别为公路网和自行车网络
  
- `Bbox_1`, `Bbox_2`变量(type: list)：
  列表类型，形式为`Bbox_1 = [经度0, 纬度0]`，`Bbox_2 = [经度1, 纬度1]`，`Bbox_1`为左下角，`Bbox_2`为右上角，尽量保证`经度0<经度1`和`纬度0<纬度1`，否则可能会发生错误。你也可以直接在`download_map_file`直接给与`Bbox_1`, `Bbox_2`变量的值，无需修改此处。
  
  config.py中设置的原始值为北京市范围。
  
4. 特别注意：
 - OSM的坐标系统为WGS-84，而绝大多数在中国的在线地图服务采取GCJ-02坐标系统，因为OSM并不使用此坐标系统，在绘图时请勿使用经过该系统处理图像及数据，若要使用务必进行转换；
 - 根据中华人民共和国测绘法规定，国家对从事测绘活动的单位实行测绘资质管理制度，个人开展未经许可的测绘则为非法，因此OSM的坐标系统会在WGS-84的基础上加入随机的偏移；
 - 有时OSM并不会提供两点间距离，为保证有向图的正确构造，两点间距离将不使用OSM中提供的数据，而根据两点的坐标计算球面两点间距离，使用地球半径为6378.137km，并且两点间距离与OSM中提供的相差极小。
 
 # 开始
 ```
 python main.py
 ```
 
 # 运行效率
 除下载文件的时间有较大变数外（与你的网络环境有关），大约40KM X 40KM的北京市路网导出会在10分钟以内完成（i7-9750H，导出`config.py`注释中的公路网示例只需大概20s），因次暂时无需实现并行，该示例的原始文件地图可从此处下载：[提取码:i4fh](https://pan.baidu.com/s/1y1iw_Ry7ZL-uQPz6C4p7wg)
 
 - [ ] TODO:multiprocessing
 
 # 结果示意
 
 ![HighwayNetwork](https://github.com/ImLaoBJie/Network_Extractor/blob/master/example/highway_map.png)
 

 使用愉快:yum:
