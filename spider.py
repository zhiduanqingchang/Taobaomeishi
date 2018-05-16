#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/4/23 21:01
# @Author  : ChenHuan
# @Site    : 
# @File    : spider.py
# @Desc    :
# @Software: PyCharm

from pyquery import PyQuery as pq
from config import *
import pymongo
import re
# 引入浏览器驱动
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

client = pymongo.MongoClient(MONGO_URL)
db = client.get_database(MONGO_DB)

# 声明一个浏览器驱动
# browser = webdriver.Chrome('E:\Install\chromedriver.exe')
# 报错selenium.common.exceptions.WebDriverException: Message: 'phantomjs.exe' executable needs to be in PATH. ,添加执行文件路径即可
browser = webdriver.PhantomJS('E:\Install\phantomjs-2.1.1-windows\\bin\phantomjs.exe', service_args=SERVICE_ARGS)
# 可将WebDriverWait(browser, 10)替换成一个变量,因为后面会在很多地方用到
wait = WebDriverWait(browser, 10)

browser.set_window_size(1400, 900)

def search():
    """定义一个搜索的方法"""
    browser.get('https://www.taobao.com')
    # 等待浏览器加载,判断是否加载成功,才能进行系一步
    # 指定一个显示条件,设置一个最长的等待时间,如果目标元素在指定时间内显示出来就会抛出异常
    # 得不到目标精会返回一个TimeoutException,利用try except捕获
    print('正在搜索')
    try:
        # 利用CSS选择器,选择搜索框(小技巧,在检查元素中选中搜索框之后,右键选择Copy再选择Copy selector),得到'#q'
        input = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#q'))
        )
        # 条件:element_to_be_clickable,按钮是可点击的
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        # 模拟操作,在输入框中输入内容
        input.send_keys(KEYWORDS)
        # 提交
        submit.click()
        # 判断页数有没有加载完成
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        # 调用获取商品信息
        get_products()
        # 返回总的页数
        return total.text
    except TimeoutException:
        # 利用递归,再次执行
        return search()

def next_page(page_number):
    """获取下一页内容"""
    print('当前翻页', page_number)
    try:
        # 输入到第几页
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > input')))
        # 点击确定
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        # 清除输入框里之前的内容
        input.clear()
        input.send_keys(page_number)
        submit.click()
        # 根据高亮区域显示数字来判断页面是否跳转成功
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
        # 跳转成功则获取该页所有商品详情
        get_products()
    except TimeoutException:
        return next_page(page_number)

def get_products():
    """定义解析方法"""
    # 判断商品内容是否加载完成,加#号代表id
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-itemlist .items .item')))
    # 得到网页源代码
    html = browser.page_source
    # 使用pyquery进行解析,获取需要的信息
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            # 图片链接
            'image': item.find('.pic .img').attr('src'),
            # 价格
            'price': item.find('.price').text().replace('\n',' '),
            # 成交量
            'deal': item.find('.deal-cnt').text()[:-3],
            # 标题
            'title': item.find('.title').text().replace('\n',' '),
            # 商铺
            'shop': item.find('.shop').text().replace('\n',' '),
            # 地点
            'location': item.find('.location').text().replace('\n',' ')
        }
        save_to_mongo(product)

def save_to_mongo(result):
    """存储到MongoDB"""
    try:
        if db[MONGO_TABLE].insert(result):
            print('存储到MongoDB成功', result)
    except Exception:
        print('存储到MongoDB错误', result)

def main():
    try:
        total = search()
        # 利用正则表达式得到页数
        total = int(re.compile('(\d+)').search(total).group(1))
        for page_number in range(2, total+1):
            next_page(page_number)
    except Exception:
        print('出错了')
    finally:
        browser.close()
"""
报错:selenium.common.exceptions.NoSuchWindowException: Message: {"errorMessage":"Unable to close window (closed already?)","request":{"headers":{"Accept":"application/json","Accept-Encoding":"identity","Connection":"close","Content-Type":"application/json;charset=UTF-8","Host":"127.0.0.1:6480","User-Agent":"Python http auth"},"httpVersion":"1.1","method":"DELETE","url":"/window","urlParsed":{"anchor":"","query":"","file":"window","directory":"/","path":"/window","relative":"/window","port":"","host":"","password":"","user":"","userInfo":"","authority":"","protocol":"","source":"/window","queryKey":{},"chunks":["window"]},"urlOriginal":"/session/094b66c0-4712-11e8-ac10-99a5037ce2fd/window"}}
Screenshot: available via screen
原因:finally最后执行browser.close()时报错,因为在try中也写了语句browser.close(),所以去掉try中的该语句.
"""

if __name__ == '__main__':
    main()
