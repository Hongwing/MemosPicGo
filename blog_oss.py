####
# 将简书中的图片 上传至memos.
####
# 1. 上传图片后获得一个返回地址
# 2. 下载该图片
# 3. cwebp 转换该图片为一个webp
# 4. 上传该webp至memos

# 简化版本
# 1. 给一个上传后的地址， 返回一个memos地址 https://memos.henryhe.cn/o/r/36

# 先调用 blob接口 上传资源

# 再调用 memo接口 携带资源生成PicGO memo.

import requests
import os
import subprocess
import json

BEARER_TOKEN = ''
HEADERS = {'Authorization': 'Bearer ' + BEARER_TOKEN}
SAVE_PATH = '/Users/henryhe'

def upload_memos(pic_url):
    save_path, image_name = download_pic(pic_url)
    print(save_path, image_name)
    save_path = cwebp_convert_pic(image_name)
    r_list = get_memos_with_id(31)
    print(r_list)
    pic_id = post_memo_blob(save_path)
    memo_pic_url = 'https://memos.henryhe.cn/o/r/'
    r_list.append(pic_id)
    print(r_list)
    result = patch_memos_with_resourcelist(31, r_list)
    print(result)
    print('\n==========================\nyour pic: \n' + memo_pic_url + str(pic_id))

def cwebp_convert_pic(name):
    origin_path = SAVE_PATH + '/' + name
    result_path = SAVE_PATH + '/' + name +'.webp'
    command = r'cwebp ' + origin_path + ' -o ' + result_path
    r_code =subprocess.Popen(command, shell=True)
    r_code.wait()
    if 'returncode: 0' in str(r_code):
        print('convert to cwebp successfully: ' + result_path)
    else:
        print('convert failed.')
    # 清楚原文件
    os.remove(origin_path)
    return result_path

def download_pic(pic_url):
    # url = 'https://upload-images.jianshu.io/upload_images/1241175-5578d60f55fac4fd.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240'
    # 过滤出url中的文件名 1241175-5578d60f55fac4fd.jpg
    image_name = pic_url.split('/')[4].split('?')[0]
    page = WebPage('s')
    page.download(pic_url, SAVE_PATH)
    return SAVE_PATH + '/' + image_name, image_name

def download_pic_request(pic_url):
    image_name = pic_url.split('/')[4].split('?')[0]
    response = requests.get(pic_url)
    if response.status_code == 200:
        with open(SAVE_PATH + '/' + image_name, 'wb') as f:
            f.write(response.content)


def get_memos_with_id(id):
    response = requests.get('https://memos.henryhe.cn/api/v1/memo/' + str(id), headers=HEADERS)
    # print(response.json().get('resourceList'))
    dic = response.json().get('resourceList')
    # 过滤当前id的memo的所有resourceList ids
    return [obj['id'] for obj in dic]

def post_memo_blob(filepath):
    # filepath: '/Users/henryhe/t.webp'
    files = {'file': open(filepath, 'rb')}
    final_resp = requests.post('https://memos.henryhe.cn/api/v1/resource/blob', files=files, headers=HEADERS)
    # 获取id
    pic_id = final_resp.json().get('id')
    return pic_id

def patch_memos_with_resourcelist(memo_id, resource_list):
    payload = {
        "id": memo_id,
        "content": "#PicGo ",
        "visibility": "PUBLIC",
        "resourceIdList": resource_list,
        "relationList": []
    }
    response = requests.patch('https://memos.henryhe.cn/api/v1/memo/' + str(memo_id), headers=HEADERS, data=json.dumps(payload))
    # print(response.json().get('resourceList'))
    dic = response.json().get('resourceList')
    return [obj['id'] for obj in dic]

### ?imageMogr2/auto-orient/strip|imageView2/2/w/400/format/webp
# upload_memos('https://upload-images.jianshu.io/upload_images/1241175-5578d60f55fac4fd.jpg?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240')
upload_memos('https://upload-images.jianshu.io/upload_images/1241175-5578d60f55fac4fd.jpg?imageMogr2/auto-orient/strip|imageView2/2/w/1200')