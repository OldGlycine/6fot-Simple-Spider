import geopandas as gpd
import os
import numpy as np
pname = ['青海', '西藏', '新疆', '宁夏', '甘肃', '陕西', '云南', '贵州', '四川',
 '重庆', '海南', '广西', '广东', '湖南', '湖北', '河南', '山东', '江西', '福建', '安徽', '浙江',
 '江苏', '上海', '黑龙江', '吉林', '辽宁', '内蒙古', '山西', '河北', '天津', '北京']

bounds = []

for name in pname:
    data = gpd.read_file(f'./shape_data/{name}.json')
    data['geometry'] = data['geometry'].buffer(0)
    data = data[data.is_valid]
    ori_bound = data['geometry'].unary_union.bounds
    bound = np.round(np.array(ori_bound), 1)
    bounds.append(bound.tolist())

print(bounds)