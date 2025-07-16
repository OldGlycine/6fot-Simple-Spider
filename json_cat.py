import json
import os
import glob

def merge_json_files(input_dir, output_file):
    # 初始化合并数据
    merged_data = {
        "type": "FeatureCollection",
        "name": "merged_features",  # 使用通用名称
        "features": []
    }
    
    # 获取目录下所有json文件
    file_pattern = os.path.join(input_dir, '*.json')
    json_files = glob.glob(file_pattern)
    
    if not json_files:
        print(f"警告: 在目录 {input_dir} 中没有找到JSON文件")
        return
    
    print(f"找到 {len(json_files)} 个JSON文件，开始合并...")
    
    # 遍历所有JSON文件
    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 验证文件结构
                if data.get('type') == 'FeatureCollection' and isinstance(data.get('features'), list):
                    merged_data['features'].extend(data['features'])
                    print(f"已添加 {len(data['features'])} 个要素来自 {os.path.basename(file_path)}")
                else:
                    print(f"警告: 文件 {os.path.basename(file_path)} 格式不符合要求，已跳过")
                    
        except Exception as e:
            print(f"处理文件 {file_path} 时出错: {str(e)}")
    
    # 写入合并结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    print(f"合并完成! 总要素数: {len(merged_data['features'])}")
    print(f"结果已保存至: {output_file}")

# 使用示例
if __name__ == "__main__":
    # 配置参数
    input_directory = "./"  # 替换为你的JSON文件目录
    output_path = "迪庆3000.json"    # 输出文件名
    
    # 执行合并
    merge_json_files(input_directory, output_path)