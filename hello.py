# -*- coding:utf-8 -*-
import os
from urllib.request import urlopen, Request, urlretrieve
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pandas import DataFrame

# 目标URL
url = 'https://english.jnu.edu.cn/about_jnu/list.htm'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

# 发送请求
ret = Request(url, headers=headers)
try:
    res = urlopen(ret)
    contents = res.read()
except Exception as e:
    print(f"请求失败: {e}")
    exit()

# 解析HTML内容
soup = BeautifulSoup(contents, "html.parser")
print("页面内容:" + "\n" + "标题        链接          图片链接")

# 创建DataFrame用于存储数据
df_ret = DataFrame(columns=["标题", "链接", "图片路径"])

# 图片保存目录
img_dir = "downloaded_images"
if not os.path.exists(img_dir):
    os.makedirs(img_dir)

count = 0
# 假设页面中的内容都在特定的标签内，比如导航栏的链接（此处根据页面结构调整）
for tag in soup.find_all('a'):  # 查找所有的<a>标签
    title = tag.get_text(strip=True)  # 获取标题文本
    url_link = tag.get('href')  # 获取链接
    if title and url_link:  # 如果标题和链接都存在
        # 查找该链接下的所有图片
        img_tags = tag.find_all_next('img')
        img_links = [urljoin(url, img.get('src')) for img in img_tags if img.get('src')]  # 处理相对路径

        # 如果有图片链接，下载图片
        img_paths = []
        for i, img_link in enumerate(img_links):
            try:
                # 获取图片文件名
                img_name = f"{title}_{i+1}.jpg"
                img_path = os.path.join(img_dir, img_name)
                urlretrieve(img_link, img_path)  # 下载图片
                img_paths.append(img_path)  # 保存图片路径
            except Exception as e:
                print(f"下载图片失败: {img_link}, 错误: {e}")
        
        # 如果下载了图片，将图片路径保存
        img_paths_str = ", ".join(img_paths) if img_paths else "无图片"
        
        print(f"{title}        {url_link}        {img_paths_str}")
        
        # 将数据添加到DataFrame中
        df_ret.loc[count] = [title, url_link, img_paths_str]  # 将标题、链接和图片路径存入DataFrame
        count += 1

# 将数据保存为CSV文件
df_ret.to_csv('jnu_about_links_with_images_downloaded.csv', encoding='gbk', index=False)

# 打印前5行数据
print(df_ret.head())
