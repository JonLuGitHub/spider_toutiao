# coding=gbk
import os
import requests
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

#定义分页的起始页数和终止页数
GROUP_START = 1
GROUP_END = 5

def get_page(offset):
    """加载单个Ajax请求的结果"""
    
    #URL后半部分参数
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery',
    }
    
    #调用urlencode()方法将参数转化为URL的GET请求参数
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    """解析数据，构造一个生成器"""
    data = json.get('data')
    if data:
        for item in data:
            # print(item)
            image_list = item.get('image_list')
            title = item.get('title')
            # print(image_list)
            if image_list:
                for image in image_list:
                    yield {
                        'image': image.get('url'),
                        'title': title
                    }

def save_image(item):
    """保存图片"""
    
    #根据item的title来创建文件夹
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    
    try:
        local_image_url = item.get('image')
        new_image_url = local_image_url.replace('list','large')
        response = requests.get('http:' + new_image_url)
        if response.status_code == 200:
            
            #图片名称使用其内容的MD5值，这样可以去除重复
            file_path = '{0}/{1}.{2}'.format(item.get('title'), \
            md5(response.content).hexdigest(), 'jpg')
            
            if not os.path.exists(file_path):
                with open(file_path, 'wb')as f:
                    f.write(response.content)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to save image')

def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)

if __name__ == '__main__':
    #利用多进程的进程池，调用其map()方法实现多进程下载
    #pool池未指定最大进程数，默认创建进程数为系统内核数
    pool = Pool() 
    #创建一个生成器
    groups = (x * 20 for x in range(GROUP_START, GROUP_END + 1))
    pool.map(main, groups)
    #关闭进程池
    pool.close()
    #等待所有子进程结束
    pool.join()
