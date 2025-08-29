# 生成每个省份每个月份的json文件，需要手动创建output文件夹
import enum
import matplotlib.pyplot as plt
import pandas as pd
import transbigdata as tbd
import geopandas as gpd
import os
import numpy as np


pname = ['青海', '西藏', '新疆', '宁夏', '甘肃', '陕西', '云南', '贵州', '四川',
 '重庆', '海南', '广西', '广东', '湖南', '湖北', '河南', '山东', '江西', '福建', '安徽', '浙江',
 '江苏', '上海', '黑龙江', '吉林', '辽宁', '内蒙古', '山西', '河北', '天津', '北京']
years = ['2023', '2024', '2025']
months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

bounds = [[89.4, 31.6, 103.1, 39.2], [78.4, 26.9, 99.1, 36.5], [73.5, 34.3, 96.4, 49.2], [104.3, 35.2, 107.7, 39.4], 
          [92.3, 32.6, 108.7, 42.8], [105.5, 31.7, 111.2, 39.6], [97.5, 21.1, 106.2, 29.2], [103.6, 24.6, 109.6, 29.2], 
          [97.4, 26.0, 108.5, 34.3], [105.3, 28.2, 110.2, 32.2], [108.6, 3.8, 117.8, 20.2], [104.5, 20.9, 112.1, 26.4], 
          [109.7, 20.2, 117.2, 25.5], [108.8, 24.6, 114.3, 30.1], [108.4, 29.0, 116.1, 33.3], [110.4, 31.4, 116.7, 36.4], 
          [114.8, 34.4, 122.7, 38.4], [113.6, 24.5, 118.5, 30.1], [115.9, 23.5, 120.7, 28.3], [114.9, 29.4, 119.6, 34.7], 
          [118.0, 27.1, 122.8, 31.2], [116.4, 30.8, 122.0, 35.1], [120.9, 30.7, 122.2, 31.9], [121.2, 43.4, 135.1, 53.6], 
          [121.6, 40.9, 131.3, 46.3], [118.8, 38.7, 125.8, 43.5], [97.2, 37.4, 126.1, 53.3], [110.2, 34.6, 114.6, 40.7], 
          [113.5, 36.0, 119.9, 42.6], [116.7, 38.6, 118.1, 40.3], [115.4, 39.4, 117.5, 41.1]]

if __name__ == '__main__':
    for index, name in enumerate(pname):
        # 创建对应文件夹
        if not os.path.exists(f"output/{name}/"):
            os.mkdir(f"output/{name}/")
        for year in years:
            for month in months:
                shp_path = './shape_data/' + name + '.json'
                if os.path.exists('./dataset/' + name + f'轨迹/{year}年/{month}月/'):
                    paths = os.listdir('./dataset/' + name + f'轨迹/{year}年/{month}月/')
                    data = pd.read_csv('./dataset/' + name + f'轨迹/{year}年/{month}月/' + paths[0], names=["timeStemp", "lat", "lng"],
                                dtype={"timeStemp": int, "lat": float, "lng": float})
                    print(f'{name}{year}年{month}月')
                    # 遍历剩余的CSV文件并拼接它们
                    counter = 0
                    for file in paths[1:]:
                        data_new = None
                        df_new = pd.read_csv('./dataset/' + name + f'轨迹/{year}年/{month}月/' + file, names=["timeStemp", "lat", "lng"],
                                dtype={"timeStemp": int, "lat": float, "lng": float})
                        df_new = df_new.dropna()
                        counter += 1
                        print('\r' + str(counter) + '/' + str(len(paths)-1) + ' now processing:' + file, end="")
                        data = pd.concat([data, df_new], ignore_index=True)
                    # print(data.shape)
                    data.to_csv('temp.csv', index=False)
                    for i in [1000, 2000, 3000, 5000, 8000]:
                        data = pd.read_csv('temp.csv')
                        shp_file = gpd.read_file(shp_path)
                        shp_file.crs = None
                        
                        # 修复无效几何
                        shp_file['geometry'] = shp_file['geometry'].buffer(0)
                        shp_file = shp_file[shp_file.is_valid]
                        if not shp_file.is_valid.all():
                            print('有无效几何')
                        data = tbd.clean_outofshape(data, shp_file, col=['lng', 'lat'], accuracy=500)
                        params = tbd.area_to_params(bounds[index], accuracy=i)
                        # 栅格化

                        data['LONCOL'], data['LATCOL'] = tbd.GPS_to_grid(data['lng'], data['lat'], params)
                        # 集记栅格数据量

                        datatest = data.groupby(['LONCOL', 'LATCOL'])['timeStemp'].count().reset_index()

                        # print(datatest)

                        # 生成栅格地理图形
                        datatest['geometry'] = tbd.grid_to_polygon([datatest['LONCOL'], datatest['LATCOL']], params)
                        # 转为GeoDataFrame
                        datatest = gpd.GeoDataFrame(datatest)

                        # print(datatest)
                        # json_path = './output/青海.json'
                        datatest.to_file(f'./output/{name}/{name}{year}年{month}月粒度{i}.json', driver="GeoJSON")
                        # datatest.to_csv('./output/青海.csv')
                        # datatest.to_file("./output/青海.shp")