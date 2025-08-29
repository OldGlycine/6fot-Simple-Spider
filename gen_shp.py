import os
from supervision import JSONSink
import transbigdata as tbd
import geopandas as gpd

pname = ['青海', '西藏', '新疆', '宁夏', '甘肃', '陕西', '云南', '贵州', '四川',
 '重庆', '海南', '广西', '广东', '湖南', '湖北', '河南', '山东', '江西', '福建', '安徽', '浙江',
 '江苏', '上海', '黑龙江', '吉林', '辽宁', '内蒙古', '山西', '河北', '天津', '北京']

if __name__ == '__main__':
    for name in pname:
        if not os.path.exists(f"shapes/{name}/"):
            os.mkdir(f"shapes/{name}/")
        for lidu in ['粒度1000', '粒度2000', '粒度3000', '粒度5000', '粒度8000']:
            if not os.path.exists(f"shapes/{name}/{lidu}"):
                os.mkdir(f"shapes/{name}/{lidu}")
            json_files = os.listdir(f'merge/{name}/{lidu}')
            for json_single in json_files:
                json_name = json_single.split('.')[0]
                if not os.path.exists(f"shapes/{name}/{lidu}/{json_name}"):
                    os.mkdir(f"shapes/{name}/{lidu}/{json_name}")
                temp = gpd.read_file(f"merge/{name}/{lidu}/{json_single}")
                temp.to_file(f"shapes/{name}/{lidu}/{json_name}/{json_name}.shp")
                              

