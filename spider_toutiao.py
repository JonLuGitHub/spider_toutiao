# coding=gbk
import os
import requests
from urllib.parse import urlencode
from hashlib import md5
from multiprocessing.pool import Pool

#�����ҳ����ʼҳ������ֹҳ��
GROUP_START = 1
GROUP_END = 5

def get_page(offset):
    """���ص���Ajax����Ľ��"""
    
    #URL��벿�ֲ���
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '����',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '3',
        'from': 'gallery',
    }
    
    #����urlencode()����������ת��ΪURL��GET�������
    url = 'https://www.toutiao.com/search_content/?' + urlencode(params)
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    except requests.ConnectionError:
        return None

def get_images(json):
    """�������ݣ�����һ��������"""
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
    """����ͼƬ"""
    
    #����item��title�������ļ���
    if not os.path.exists(item.get('title')):
        os.mkdir(item.get('title'))
    
    try:
        local_image_url = item.get('image')
        new_image_url = local_image_url.replace('list','large')
        response = requests.get('http:' + new_image_url)
        if response.status_code == 200:
            
            #ͼƬ����ʹ�������ݵ�MD5ֵ����������ȥ���ظ�
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
    #���ö���̵Ľ��̳أ�������map()����ʵ�ֶ��������
    #pool��δָ������������Ĭ�ϴ���������Ϊϵͳ�ں���
    pool = Pool() 
    #����һ��������
    groups = (x * 20 for x in range(GROUP_START, GROUP_END + 1))
    pool.map(main, groups)
    #�رս��̳�
    pool.close()
    #�ȴ������ӽ��̽���
    pool.join()
