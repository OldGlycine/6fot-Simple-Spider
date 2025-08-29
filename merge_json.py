import json
import os

pname = ['青海', '西藏', '新疆', '宁夏', '甘肃', '陕西', '云南', '贵州', '四川',
 '重庆', '海南', '广西', '广东', '湖南', '湖北', '河南', '山东', '江西', '福建', '安徽', '浙江',
 '江苏', '上海', '黑龙江', '吉林', '辽宁', '内蒙古', '山西', '河北', '天津', '北京']

# 一年是2023.03-2024.02 和 2024.03-2025.02
# 两年整体一套，1个数据集
# 四季，两年春夏秋冬合一套，第一年春夏秋冬一套，第二年春夏秋冬一套。12个数据集
# 1km\2km\3km\5km\8km

def merge_json_files(json_files, output_file, name):
    # 初始化合并数据
    merged_data = {
        "type": "FeatureCollection",
        "name": name,  # 使用通用名称
        "features": []
    }
    print(name)
    # 遍历所有JSON文件
    for index, file_path in enumerate(json_files):
        print('\r' + f'目前处理{file_path},进度{index + 1}/{len(json_files)}', end='')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 验证文件结构
                if data.get('type') == 'FeatureCollection' and isinstance(data.get('features'), list):
                    merged_data['features'].extend(data['features'])
                    
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    print()
    # 写入合并结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False)

if __name__ == '__main__':
    for name in pname:
        all_files = os.listdir(f'./output/{name}')
        if not os.path.exists(f"merge/{name}/"):
            os.mkdir(f"merge/{name}/")
        for lidu in ['粒度1000', '粒度2000', '粒度3000', '粒度5000', '粒度8000']:
            if not os.path.exists(f"merge/{name}/{lidu}"):
                os.mkdir(f"merge/{name}/{lidu}")
            lidu_files = [f'./output/{name}/' + i for i in all_files if lidu in i]
            lidu_files.sort()

            merge_name = f'{name}第一年春季.json'
            merge_files = []
            for i in range(0, 12, 12):
                merge_files.extend(lidu_files[i:i+3])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第一年夏季.json'
            merge_files = []
            for i in range(0, 12, 12):
                merge_files.extend(lidu_files[i+3:i+6])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第一年秋季.json'
            merge_files = []
            for i in range(0, 12, 12):
                merge_files.extend(lidu_files[i+6:i+9])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第一年冬季.json'
            merge_files = []
            for i in range(0, 12, 12):
                merge_files.extend(lidu_files[i+9:i+12])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第二年春季.json'
            merge_files = []
            for i in range(12, 24, 12):
                merge_files.extend(lidu_files[i:i+3])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第二年夏季.json'
            merge_files = []
            for i in range(12, 24, 12):
                merge_files.extend(lidu_files[i+3:i+6])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第二年秋季.json'
            merge_files = []
            for i in range(12, 24, 12):
                merge_files.extend(lidu_files[i+6:i+9])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}第二年冬季.json'
            merge_files = []
            for i in range(12, 24, 12):
                merge_files.extend(lidu_files[i+9:i+12])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}两年春季.json'
            merge_files = []
            for i in range(0, 24, 12):
                merge_files.extend(lidu_files[i:i+3])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}两年夏季.json'
            merge_files = []
            for i in range(0, 24, 12):
                merge_files.extend(lidu_files[i+3:i+6])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}两年秋季.json'
            merge_files = []
            for i in range(0, 24, 12):
                merge_files.extend(lidu_files[i+6:i+9])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}两年冬季.json'
            merge_files = []
            for i in range(0, 24, 12):
                merge_files.extend(lidu_files[i+9:i+12])
            merge_json_files(merge_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])

            merge_name = f'{name}两年.json'
            merge_json_files(lidu_files, f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])
            merge_name = f'{name}第一年.json'
            merge_json_files(lidu_files[:12], f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])
            merge_name = f'{name}第二年.json'
            merge_json_files(lidu_files[12:], f'./merge/{name}/{lidu}/{merge_name}', merge_name.split('.')[0])
        