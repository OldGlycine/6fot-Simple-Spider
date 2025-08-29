import os
import csv

pname = ['青海', '西藏', '新疆', '宁夏', '甘肃', '陕西', '云南', '贵州', '四川',
 '重庆', '海南', '广西', '广东', '湖南', '湖北', '河南', '山东', '江西', '福建', '安徽', '浙江',
 '江苏', '上海', '黑龙江', '吉林', '辽宁', '内蒙古', '山西', '河北', '天津', '北京']

if __name__ == '__main__':
    for name in pname:
        base_dir = f'./dataset/{name}轨迹'
        with open('./test.csv', mode='a', newline='', encoding='utf-8') as csv_file:
            csv_writer = csv.writer(csv_file)
            write_header = not os.path.exists('./test.csv') or os.stat('./test.csv').st_size == 0
            # 使用列表推导式获取所有二级子目录中的数字
            numbers = [
                int(file.split('轨迹')[0])
                for year_dir in os.listdir(base_dir)
                    if os.path.isdir(year_path := os.path.join(base_dir, year_dir))
                    for month_dir in os.listdir(year_path)
                        if os.path.isdir(month_path := os.path.join(year_path, month_dir))
                        for file in os.listdir(month_path)
                            if file.endswith('轨迹.csv')
            ]

            print(f"{name}全部数据量{len(numbers)}")  # 输出结果列表
            if write_header:
                csv_writer.writerow(['name', 'year', 'month', 'count'])
            csv_writer.writerow([name, '总', '总', len(numbers)])

            months = [
                f'./dataset/{name}轨迹/' + year_dir + '/' + month_dir
                for year_dir in os.listdir(base_dir)
                    if os.path.isdir(year_path := os.path.join(base_dir, year_dir))
                    for month_dir in os.listdir(year_path)
                        if os.path.isdir(month_path := os.path.join(year_path, month_dir))
            ]
            for month in months:
                month_file = os.listdir(month)
                print(f'{name}{month.split("/")[-2:]}数量:\n{len(month_file)}')

                if write_header:
                    csv_writer.writerow(['name', 'year', 'month', 'count'])
                csv_writer.writerow([name, month.split("/")[-2], month.split("/")[-1], len(month_file)])