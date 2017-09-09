import re
import numpy as np
from bs4 import BeautifulSoup
from pymongo import MongoClient


cities = {
    'bj': '北京', 'sh': '上海', 'gz': '广州', 'sz': '深圳',
    'cs': '长沙', 'wh': '武汉', 'cd': '成都', 'cq': '重庆'
}


#添加一个回调函数类,解析详情页的数据信息，并且将数据信息保存到mongodb数据库中去
class GetDetailInfo:
    def __init__(self, client=None):
        self.client = MongoClient('localhost', 27017) if client is None else client
        self.db = self.client.xiaozhu


    def __call__(self, url, html):
        if re.search('/fangzi/', url):
            soup = BeautifulSoup(html, 'lxml')
            # 解析数据
            city = cities.get(url.split("//")[1].split(".")[0])
            try:
                title = soup.select('div.pho_info h4 em')[0].get_text()
            except Exception:
                title = np.nan
            try:
                address = soup.select('div.pho_info p')[0].get('title')
            except Exception:
                address = np.nan
            try:
                rent_cost_day = int(soup.select('div.day_l span')[0].get_text())
            except Exception:
                rent_cost_day = np.nan
            try:
                sex_landlord = soup.select('div.member_pic div')
                sex_landlord = 'Female' if sex_landlord[0].get('class')[0] == 'member_ico1' else 'Male'
            except Exception:
                sex_landlord = np.nan
            try:
                name_landlord = soup.select('a.lorder_name')[0].get_text()
            except Exception:
                name_landlord = np.nan
            try:
                rate = soup.select('li.top_bar_w2.border_right_none em.score-rate')[0].get_text()
            except Exception:
                rate = np.nan
            try:
                house_info = soup.select('#introduce p')[0].get_text().split(' ')
                area = house_info[0].split('：')[-1]
                layout = house_info[-1].split('：')[-1]
            except Exception:
                area = np.nan
                layout = np.nan
            try:
                sumpeople = soup.select('#introduce h6.h_ico2')[0].get_text()
            except Exception:
                sumpeople = np.nan
            try:
                beds = soup.select('#introduce h6.h_ico3')[0].get_text()
            except Exception:
                beds = np.nan
            data = {
                'city': city, 'link': url, 'title': title, 'address': address, 'rent_cost_day': rent_cost_day,
                'sex_landlord': sex_landlord, 'name_landlord': name_landlord, 'rate': rate,
                'sumpeople': sumpeople, 'beds': beds, 'layout': layout, 'area': area,
            }
            self.db.house_info.insert_one(data)
        else:
            pass
