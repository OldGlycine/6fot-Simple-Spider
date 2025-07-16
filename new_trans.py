import matplotlib.pyplot as plt
import pandas as pd
import transbigdata as tbd
import geopandas as gpd
import os
import yaml
from configs import * 

config = yaml.safe_load(open('configs/cfg.yaml', encoding='UTF-8'))
cfg = from_dict(config)

# 这里和shape_data文件夹的经纬度和json文件，需要手动补充
pname = ['青海', '四川','西藏']
bounds = [ [89.6, 31.6, 103.0, 39.2],
            [97.4, 26.0, 108.6, 34.3],
            [78.4, 26.8, 99.1, 36.9]
        ]
# 是否是徒步数据
is_walk = cfg.on_foot

if __name__ == '__main__':
    for index, name in enumerate(pname):
        shp_path = './shape_data/' + name + '.json'
        paths = None
        if not is_walk:
            paths = os.listdir('./dataset/' + name + '轨迹/')
        else:
            paths = os.listdir('./dataset/' + name + '徒步轨迹/')
        all_path = './dataset/' + name + '.csv'
        
        # 如果csv文件过大，则需要分批处理，step为每次处理多少个csv文件
        flag = 0
        step = 50
        while flag < len(paths):
            data = None
            if not is_walk:
                data = pd.read_csv('./dataset/' + name + '轨迹/' + paths[flag], names=["timeStemp", "lat", "lng", "height", "speed", "km"],
                            dtype={"timeStemp": int, "lat": float, "lng": float, "height": float,
                                    "speed": float, "km": float})
            else:
                data = pd.read_csv('./dataset/' + name + '徒步轨迹/' + paths[flag], names=["timeStemp", "lat", "lng", "height", "speed", "km"],
                            dtype={"timeStemp": int, "lat": float, "lng": float, "height": float,
                                    "speed": float, "km": float})
            
            # 遍历剩余的CSV文件并拼接它们
            counter = 0
            tralen = min(flag + step, len(paths))
            print(flag, tralen)
            for file in paths[flag + 1:tralen]:
                data_new = None
                if not is_walk:
                    df_new = pd.read_csv('./dataset/' + name + '轨迹/' + file, names=["timeStemp", "lat", "lng", "height", "speed", "km"],
                                dtype={"timeStemp": float, "lat": float, "lng": float, "height": float,
                                        "speed": float, "km": float})
                else:
                    df_new = pd.read_csv('./dataset/' + name + '徒步轨迹/' + file, names=["timeStemp", "lat", "lng", "height", "speed", "km"],
                                dtype={"timeStemp": float, "lat": float, "lng": float, "height": float,
                                        "speed": float, "km": float})
                df_new = df_new.dropna()
                counter += 1
                print('\r' + str(flag + counter) + '/' + str(flag + step - 1) + ' now processing:' + file, end="")
                data = pd.concat([data, df_new], ignore_index=True)
            flag += step
            print(data)
            for i in [3000, 5000, 8000, 10000]:
                json_path = None
                if not is_walk:
                    json_path = all_path.split('.')[0] + name + str(i) + '_' + str(flag) + ".json"
                else:
                    json_path = all_path.split('.')[0] + name + '徒步' +  str(i) + '_' + str(flag) + ".json"
                # tbd.visualization_data(data, col=['lng', 'lat'])
                print(2)
                shp_file = gpd.read_file(shp_path)
                shp_file.crs = None
                # 修复无效几何
                print(3)
                shp_file['geometry'] = shp_file['geometry'].buffer(0)
                shp_file = shp_file[shp_file.is_valid]
                if not shp_file.is_valid.all():
                    print('有无效几何')
                data = tbd.clean_outofshape(data, shp_file, col=['lng', 'lat'], accuracy=500)
                # data = tbd.clean_taxi_status(data, col=["pointID", "speed", "time", "url"])
                print(4)
                params = tbd.area_to_params(bounds[index], accuracy=i)
                # 栅格化
                print(5)
                data['LONCOL'], data['LATCOL'] = tbd.GPS_to_grid(data['lng'], data['lat'], params)
                # 集记栅格数据量
                print(6)
                datatest = data.groupby(['LONCOL', 'LATCOL'])['timeStemp'].count().reset_index()

                # print(datatest)

                # 生成栅格地理图形
                datatest['geometry'] = tbd.grid_to_polygon([datatest['LONCOL'], datatest['LATCOL']], params)
                # 转为GeoDataFrame
                datatest = gpd.GeoDataFrame(datatest)

                print(datatest)

                # datatest.to_file(json_path, driver="GeoJSON")
                # datatest.to_csv('青海.csv')
                datatest.to_file(json_path.split('.')[0] + ".shp", driver='ESRI Shapefile')
                
                # TODO：可视化图片展示
                datatest.plot()
                plt.show()
            # except:
            #     continue