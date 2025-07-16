import re
import os
import json
import time
import requests
import datetime
import pandas as pd
from lxml import etree
from fake_useragent import UserAgent
import yaml
from configs import * 
from gen_kwd import gen
from bs4 import BeautifulSoup
import csv

# Init
config = yaml.safe_load(open('configs/cfg.yaml', encoding='UTF-8'))
cfg = from_dict(config)

swords = cfg.swords
if not cfg.on_foot:
    # 90%数据量的标签
    swords = [False, 'hiking/', 'mountaineering/', 'biking/', 'driving/', 'running/']
else:
    # 仅步行
    swords = [True, 'hiking/', 'running/']
pnum = cfg.pnum
pname = cfg.pname

# 前缀（不变的）
part1 = 'http://www.foooooot.com/search/trip/'
# 爬全省的两种网址（基本全覆盖）
part2 = ['all/create_time/ascent/', 'all/create_time/descent/']
# part2 = ['all/create_time/descent/']
# 页码限制
pages = [i for i in range(1, 101)]

# 爬虫检查点
ckpt = yaml.safe_load(open('configs/checkpoints.yaml', encoding='UTF-8'))

def save_ckpt():
    with open('configs/checkpoints.yaml', 'w') as file:
        yaml.safe_dump(ckpt, file, default_flow_style=False)

def save_fatalpoints():
    with open('configs/fatalpoints.yaml', 'w') as file:
        yaml.safe_dump(ckpt, file, default_flow_style=False)

def download_image(img_url, folder, img_id, track_id):
    """下载图片到指定文件夹"""
    try:
        img_data = requests.get(img_url, headers=headers, timeout=(10,10))
        if img_data.status_code == 200:
            if not os.path.exists(f"{folder}/{track_id}/"):
                os.mkdir(f"{folder}/{track_id}/")
            with open(f"{folder}/{track_id}/{img_id}.jpg", 'wb') as handler:
                handler.write(img_data.content)
            # print('\r'+ f"Downloaded image {img_id}.jpg in {folder}", end="")
        else:
            print(f"Failed to download image from {img_url}, status code: {img_data.status_code}")
    except Exception as e:
        print(f"Error downloading image {img_url}: {e}")
    # time.sleep(3)

def save_data(file_name, track_num_arr, trackjsons, trackimages):
    # 先判断file是否已经存在
    search_dir = None
    if not swords[0]:
        search_dir = f'./dataset/{file_name}轨迹/'
    else:
        search_dir = f'./dataset/{file_name}徒步轨迹/'
    
    files = [
        int(file.split('轨迹')[0])
        for year_dir in os.listdir(search_dir)
            if os.path.isdir(year_path := os.path.join(search_dir, year_dir))
            for month_dir in os.listdir(year_path)
                if os.path.isdir(month_path := os.path.join(year_path, month_dir))
                for file in os.listdir(month_path)
                    if file.endswith('轨迹.csv')
    ]
    for track_num, trackjson, footPrintImages in zip(track_num_arr, trackjsons, trackimages):
        # 已存在的数据不进行二次爬取，节省资源
        if int(track_num) in files:
            print('\r' + f'Skipping 轨迹{track_num}', end="")
            continue
        df1 = pd.DataFrame(trackjson)
        df1 = df1.iloc[:, :3]
        dt = datetime.datetime.fromtimestamp(int(df1.iloc[:, 0][0]))
        dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        year = dt.split('-')[0]
        month = dt.split('-')[1]
        # if ckpt['part2'] =='all/create_time/descent/' and year <= '2022' and year != '2010':
        #     return False
        # 自行更改条件，下面的过滤是基于年份
        if year in cfg.years:
            if year == '2023' and month not in ['03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
                continue
            if year == '2025' and month not in ['01', '02']:
                continue
            # 存轨迹数据部分
            path_word = None
            if not swords[0]:
                if not os.path.exists(f"./dataset/{file_name}轨迹/{year}年"):
                    os.mkdir(f"./dataset/{file_name}轨迹/{year}年")
                if not os.path.exists(f"./dataset/{file_name}轨迹/{year}年/{month}月"):
                    os.mkdir(f"./dataset/{file_name}轨迹/{year}年/{month}月")
                path_word = f"./dataset/{file_name}轨迹/{year}年/{month}月/{str(track_num)}轨迹.csv"
            else:
                if not os.path.exists(f"./dataset/{file_name}徒步轨迹/{year}年"):
                    os.mkdir(f"./dataset/{file_name}徒步轨迹/{year}年")
                if not os.path.exists(f"./dataset/{file_name}徒步轨迹/{year}年/{month}月"):
                    os.mkdir(f"./dataset/{file_name}徒步轨迹/{year}年/{month}月")
                path_word = f"./dataset/{file_name}徒步轨迹/{year}年/{month}月/{str(track_num)}轨迹.csv"

            # 存图片部分
            image_folder_name = None
            image_csv_path = None
            if not swords[0]:
                image_folder_name = f'images/{file_name}图片/{year}年'
                if not os.path.exists(image_folder_name):
                    os.mkdir(image_folder_name)
                image_folder_name = f'images/{file_name}图片/{year}年/{month}月'
                image_csv_path = image_folder_name + f"/汇总信息.csv"
                if not os.path.exists(image_folder_name):
                    os.mkdir(image_folder_name)
            else:
                image_folder_name = f'images/{file_name}徒步图片/{year}年'
                if not os.path.exists(image_folder_name):
                    os.mkdir(image_folder_name)
                image_folder_name = f'images/{file_name}徒步图片/{year}年/{month}月'
                image_csv_path = image_folder_name + f"/汇总信息.csv"
                if not os.path.exists(image_folder_name):
                    os.mkdir(image_folder_name)
            with open(image_csv_path, mode='a', newline='', encoding='utf-8') as csv_file:
                csv_writer = csv.writer(csv_file)
                write_header = not os.path.exists(image_csv_path) or os.stat(image_csv_path).st_size == 0
                if write_header:
                    csv_writer.writerow(["Image ID", "Latitude", "Longitude", "Timestamp"])
                for wrapper in footPrintImages:
                    img_tag = wrapper.find('img')
                    if img_tag and img_tag.has_attr('src') and img_tag.has_attr('pid'):
                        img_url = img_tag['src']
                        img_id = img_tag['pid']
                        lat = img_tag.get('lat')
                        lng = img_tag.get('lng')
                        timestamp = wrapper.find_next('span', style="margin-left:20px;").text.split("时间：")[
                            1] if wrapper.find_next('span', style="margin-left:20px;") else None
                        print('\r' + f"Downloading image {img_id} of Track_id {track_num}", end="")
                        if not os.path.exists(f"{image_folder_name}/{track_num}/{img_id}.jpg"):
                            download_image(img_url, image_folder_name, img_id, track_num)
                            csv_writer.writerow([img_id, lat, lng, timestamp])

            # 先下载图片再存csv
            df1.to_csv(
                path_word,
                mode="a",
                header=False,
                index=False,
                encoding="utf-8-sig",
            )

            if not swords[0]:
                print('\r' + f"{file_name}轨迹{track_num} is over!!!", end="")
            else:
                print('\r' + f"{file_name}徒步轨迹{track_num} is over!!!", end="")
        else:
            print('\r'+f'Skipping {track_num}', end='')
    return True
        
def get_id(track_num_arr, file_name):
    trackjsons = []
    trackimages = []
    bflag = True
    for track_num in track_num_arr:
        trackjson_url = f"http://www.foooooot.com/trip/{str(track_num)}/trackjson/"
        trackimage_url = f"http://www.foooooot.com/trip/{str(track_num)}/"
        try:
            track_list = requests.get(trackjson_url, headers=headers).text
            trackjson = json.loads(track_list)
            trackjsons.append(trackjson)
            
            image_list = requests.get(trackimage_url, headers=headers)
            soup = BeautifulSoup(image_list.text, "html.parser")
            footPrintImages = soup.find_all('li', class_='footPrintImage')
            trackimages.append(footPrintImages)
            bflag = save_data(file_name, track_num_arr, trackjsons, trackimages)
            
        except Exception as e:
            print(e)
    
    return bflag
               
def get_data(file_name, file_number, session):
    counter = 0
    for kwd in keyword[keyword.index(ckpt['kwd']):]:
        print(f'Now searching kwd:{kwd}')
        ckpt['kwd'] = kwd
        save_ckpt()
        for parts in part2[part2.index(ckpt['part2']):]:
            print(f'--Part2:{parts}')
            ckpt['part2'] = parts
            save_ckpt()
            for ways in swords[swords.index(ckpt['swords']):]:
                print(f'----Ways:{ways}')
                ckpt['swords'] = ways
                save_ckpt()
                bflag = True
                for page in pages[pages.index(ckpt['pages']):]:
                    ckpt['pages'] = page if page!=100 else 1
                    save_ckpt()
                    while True:
                        url = part1 + ways + file_number + parts
                        print(f'Now spidering url:{url}')
                        headers["Cookie"] = session
                        params = {
                            "page": page,
                            "keyword": kwd,
                        }
                        try:
                            res = requests.get(url, headers=headers, params=params)
                            if res.status_code == 200:
                                tree = etree.HTML(res.text)
                                trip_list = tree.xpath('//p[@class="trip-title"]/a/@href')    
                                track_num_arr = [trip.split("/")[2] for trip in trip_list]
                                if len(track_num_arr) <= 1:
                                    counter += 1
                                if counter > cfg.early_stop:
                                    counter = 0
                                    bflag = False
                                    break
                                if counter <= cfg.early_stop:
                                    bflag = get_id(track_num_arr, file_name)
                                break
                        except Exception as e:
                            print(f'Breaking loop: {e}')
                            bflag = False
                    ckpt['kwd'] = 0 if (page == pages[-1] or bflag==False) and ways == swords[-1] and parts == part2[-1] and kwd == keyword[-1] else ckpt['kwd']
                    ckpt['part2'] = part2[0] if (page == pages[-1] or bflag==False) and ways == swords[-1] and parts == part2[-1] else ckpt['part2']
                    ckpt['swords'] = swords[1] if (page == pages[-1] or bflag==False) and ways == swords[-1] else ckpt['swords']
                    ckpt['pages'] = 1 if bflag==False else ckpt['pages']
                    save_ckpt() 
                    if bflag is False:
                        break
                    print('\r' + f"kwd:{kwd}, part2:{parts}, swords:{ways}, page:{page} is over!!!")
                    time.sleep(5)

def get_sessionid(file_name, file_number, csrf):
    headers["Cookie"] = f"csrftoken={csrf}"
    data = {
        #email和password替换成登录六只脚网站的账号密码
        "csrfmiddlewaretoken": csrf,
        "email": "your user ID",
        "password": "your password",
        "next": "/accounts/login_complete/",
    }
    res = requests.post(url, headers=headers, data=data)
    session = res.request.headers["Cookie"]
    get_data(file_name, file_number, session)

def get_csrfmiddlewaretoken(file_name, file_number):
    res = requests.get(url, headers=headers)
    reg = re.compile(
        r"<div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='(.*?)' /></div>"
    )
    csrf = reg.findall(res.text)[0]
    get_sessionid(file_name, file_number, csrf)

if __name__ == "__main__":
    for cpname, cpnum in zip(pname[pname.index(ckpt['pname']):], pnum[pnum.index(ckpt['pnum']):]):
        ckpt['pname'] = cpname
        ckpt['pnum'] = cpnum
        save_ckpt()
        print(ckpt['pname'], ckpt['pnum'])

        keyword = gen(cfg.years, cpname)
        ckpt['pages'] = 1 if ckpt['kwd'] == 0 else ckpt['pages']
        ckpt['kwd'] = keyword[0] if ckpt['kwd'] == 0 else ckpt['kwd']
        ckpt['part2'] = 'all/create_time/ascent/' if ckpt['kwd'] == 0 else ckpt['part2']
        if ckpt['kwd'] == keyword[0]:
            ckpt['part2'] = 'all/create_time/descent/'
        ckpt['swords'] = swords[1] if ckpt['kwd'] == 0 else ckpt['swords']
        save_ckpt()
        print(f'keyword{keyword},cur kwd{ckpt["kwd"]}')
        

        # 创建目标文件夹
        if not swords[0]:
            if not os.path.exists(f"./dataset/{ckpt['pname']}轨迹"):
                os.mkdir(f"./dataset/{ckpt['pname']}轨迹")
            if not os.path.exists(f"./images/{ckpt['pname']}图片"):
                os.mkdir(f"./images/{ckpt['pname']}图片")
        else:
            if not os.path.exists(f"./dataset/{ckpt['pname']}徒步轨迹"):
                os.mkdir(f"./dataset/{ckpt['pname']}徒步轨迹")
            if not os.path.exists(f"./images/{ckpt['pname']}徒步图片"):
                os.mkdir(f"./images/{ckpt['pname']}徒步图片")
        url = "http://www.foooooot.com/accounts/login/"
        headers = {
            "User-Agent": UserAgent().random,
        }
        get_csrfmiddlewaretoken(ckpt['pname'], ckpt['pnum'])
        # break