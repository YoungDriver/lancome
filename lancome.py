#!/user/bin/python
#-*- coding:UTF-8 -*-
#filename = lancome.py
#version = 1.0
#author:lee

import re
import time
import urllib2
import csv
import json
import cookielib

from selenium import webdriver
from bs4 import BeautifulSoup

headers = {'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:56.0) Gecko/20100101 Firefox/56.0','Accept':'*/*','Accept-Encoding':'gzip, deflate, br','Accept-Language':'en-US,en;q=0.5','Connection':'keep-alive','Host':'gm.mmstat.com','Referer':'https://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.36.67e5a0ac%20%20%20%20DcwvXD&id=43248581241&skuId=75236709372&standard=1&user_id=2360209412&cat_id=2&is_b=1&r%20%20%20%20n=846da57ac65dad86b3d749edca7bbf39'}

http_proxy = {'http:':'139.224.24.26:8888'}

field = ['店铺号','商品名称','价格','净含量','库存','商品评分','累计评论','网址']
lancome_info = []
lancome_infos = []
def get_titleInfo(bs):
	title = bs.find('h1',{"data-spm":"1000983"})
	title = title.get_text().strip()
	title = title.encode('utf-8')
	#print title
	lancome_info.append(title)
	return title

def get_shopIdInfo(bs):
	shopIds = bs.find_all('div',itemid = re.compile(u'[0-9]{9,11}'))
	for shopId in shopIds:
		if 'shopid' in shopId.attrs:
			shopIdTmp = shopId.attrs['shopid']
	lancome_info.append(shopIdTmp)
	return shopIdTmp

def get_itemIdInfo(bs):
	items = bs.find_all('div',itemid = re.compile(u'[0-9]{11}'))
	for item in items:
		if 'itemid' in item.attrs:
			return item.attrs['itemid']

def get_urlInfo(url):
	lancome_info.append(url)

def get_scoreInfo(bs,itemid):
	score_url  = 'https://dsr-rate.tmall.com/list_dsr_info.htm?itemId=' + itemid
	score_html = urllib2.urlopen(score_url).read()
	score_html = str(score_html)
	#获取评分
	score_pat  = re.compile(u'"gradeAvg":[0-9][.][0-9]')
	score      = re.findall(score_pat,score_html)
	score      = score[0][11:]
	lancome_info.append(score)
	#print score
	#获取评论数
	comment_pat = re.compile(u'"rateTotal":[0-9]+')
	comment     = re.findall(comment_pat,score_html)
	comment     = comment[0][12:]
	lancome_info.append(comment)
	#print comment


def get_priceInfo(bs,itemid):
	js_url = 'http://ext-mdskip.taobao.com/extension/queryTmallCombo.do?itemId=' + itemid + '&comboGroup=0'
	js_html = urllib2.urlopen(js_url).read().decode('gbk')
	js_json = json.loads(js_html)
	item_id_pat = re.compile(u'[0-9]{12}')
	item_ids = re.findall(item_id_pat,js_url)
	for item_id in item_ids:
		#获取价格
		#print item_id
		item_price = js_json['currentCombo']['items'][item_id]['price']
	lancome_info.append(item_price)
	#获取含量ml
	vol_dict = js_json['currentCombo']['items'][item_id]['prop']
	vol_str  = str(vol_dict)
	vol_pat  = re.compile(u'[0-9]{1,3}ml')
	vols	 = re.findall(vol_pat,vol_str)
	for vol in vols:
		#print vol
		vol = vol
	lancome_info.append(vol)
	#获取库存
	stock    = js_json['currentCombo']['items'][item_id]['showQuantity']
	lancome_info.append(stock)
	return lancome_info

def save_lancomeInfo(info,writePt):
	#print field
	#print info
	dictval = dict(zip(field,info))
	#print dictval
	writePt.writerow(dictval) 
	del info[:]

def open_lancomeInfo():
	openFile = open('/home/lee/test/test_taobao/lancome.csv','w')
	writePt  = csv.DictWriter(openFile,field)
	writePt.writeheader()
	#dictval = dict(zip(field,info))
	#writePt.writerow(dictval)
	return writePt

def close_lancomeInfo():
	openFile.close()

def get_lancomeInfo(url):
	html = urllib2.urlopen(url).read()
	bs = BeautifulSoup(html,'lxml')
	get_shopIdInfo(bs)
	print 1
	itemid = get_itemIdInfo(bs)
	print 2
	get_titleInfo(bs)
	print 3
	get_priceInfo(bs,itemid)
	print 4
	get_scoreInfo(bs,itemid)
	print 5
	get_urlInfo(url)
	print 6
	return lancome_info

def get_lancomeAllGoodsURL(url):
	lists_url = set()
	html = get_htmlInfo(url)
	bs = BeautifulSoup(html,'lxml')
	lists = bs.find_all('dl',class_='item')
	print lists
	for listId in lists:
		newListId = '//detail.tmall.com/item.htm?id='+str(listId['data-id'])
		if newListId not in lists_url:
			newlist = 'http:'+ newListId
			print newlist
			lists_url.add(newlist)
	return lists_url

def get_lancomeAllGoodsURLBySelenium(url):
	lists_url = set()
	cookie_list = []
	cookies = cookielib.CookieJar()
	handler=urllib2.HTTPCookieProcessor(cookies)
	opener = urllib2.build_opener(handler)
	response = opener.open(url)
	for cookie in cookies:
		cookie_list.append(cookie.domain)
		cookie_list.append(cookie.name)
		cookie_list.append(cookie.value)
		cookie_list.append(cookie.path)
	headname = ['domain','name','value','path','expiry','httpOnly','secure']
	cookie_ext = [None,False,False]
	cookie_cnt = len(cookie_list)/4


	driver = webdriver.Firefox()
	driver.delete_all_cookies()
	time.sleep(3)
	driver.get(url)
	for i in range(cookie_cnt):
		cookie_tmp = cookie_list[4*i:4*(i+1)]
		cookie_tmp.extend(cookie_ext)
		cookie = dict(zip(headname,cookie_tmp))
		driver.add_cookie(cookie)
		print cookie
	time.sleep(5)
	driver.refresh()
	time.sleep(5)
	i = 1
	j = 1
	while True:
		try:
			pattern = u"//div[@class='J_TItems']/div["+str(i)+ u']/dl[' + str(j) + u']'
			url_id  = driver.find_element_by_xpath(pattern)
			url_id  = url_id.get_attribute('data-id')
			if url_id not in lists_url:
				lists_url.add(url_id)
			while True:
				try:
					j = j + 1
					pattern = u"//div[@class='J_TItems']/div["+str(i)+ u']/dl[' + str(j) + u']'
					url_id  = driver.find_element_by_xpath(pattern)
					url_id  = url_id.get_attribute('data-id')
					if url_id not in lists_url:
						lists_url.add(url_id)
				except:
					i = i + 1
					j = 1
					break
		except:
			break
	driver.close()
	return lists_url

def get_htmlInfo(url):
	cookie = cookielib.CookieJar()
	handler = urllib2.HTTPCookieProcessor(cookie)
	opener = urllib2.build_opener(handler)
	opener.add_handler(urllib2.ProxyHandler(http_proxy))

	#req = urllib2.Request(url,headers = headers)
	req = urllib2.Request(url)
	response = opener.open(req)
	html = response.read()
	return html

if __name__ == '__main__':
	writePt = open_lancomeInfo()
	url = 'https://lancome.tmall.com/search.htm?spm=a1z10.1-b-s.w5001-14640892182.3.f88c76b3vlHK2&scene=taobao_shop'
	s = get_lancomeAllGoodsURLBySelenium(url)
	#lists = get_lancomeAllGoodsURL(url)
	print s
	#for url in lists:
		#info= get_lancomeInfo(url)
		#print info
		#time.sleep(2)
		#infonew = lancome_infos.append(info)
		#print infonew
		#save_lancomeInfo(infonew,writePt)
		#dictval = dict(zip(field,infonew))
		#print infonew
		#writePt.writerow(dictval)
		#infonew.clear()
