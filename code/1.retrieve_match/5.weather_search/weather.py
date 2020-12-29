''''''
import re
import pymysql
import requests
import json
from bs4 import BeautifulSoup

# f = open('city.json', 'rb')
class SearchWeather:
    def __init__(self, cities):
        self.HEADERS ={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 ''(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        # self.CONNECTION = pymysql.connect(host='localhost',user='root',password='xxx',db='xxx',charset='utf8',cursorclass=pymysql.cursors.DictCursor)
        self.cities = cities
    def getcityCode(self,cityName):
        city_id = self.cities.get(cityName)
        return city_id
        # SQL = "SELECT cityCode FROM cityWeather WHERE cityName='%s'" % cityName
        # try:
        #     with self.CONNECTION.cursor() as cursor:
        #         cursor.execute(SQL)
        #         self.CONNECTION.commit()
        #         result = cursor.fetchone()
        #         return result['cityCode']
        # except Exception as e:
        #     print(repr(e))

    def getWeather(self,cityCode,cityname):
        url = 'http://www.weather.com.cn/weather/%s.shtml' % cityCode
        html = requests.get(url,headers = self.HEADERS)
        html.encoding='utf-8'
        soup=BeautifulSoup(html.text,'lxml')
        weather = "日期      天气    【温度】    风向风力\n"
        for item in soup.find("div", {'id': '7d'}).find('ul').find_all('li'):
            date,detail = item.find('h1').string, item.find_all('p')
            title = detail[0].string
            templow = detail[1].find("i").string
            temphigh = detail[1].find('span').string if detail[1].find('span')  else ''
            wind,direction = detail[2].find('span')['title'], detail[2].find('i').string
            if temphigh=='':
                weather += '你好，【%s】今天白天：【%s】，温度：【%s】，%s：【%s】\n' % (cityname,title,templow,wind,direction)
            else:
                weather += (date + title + "【" + templow +  "~"+temphigh +'°C】' + wind + direction + "\n")
        return weather

    def predict_(self,city):
        cityCode = self.getcityCode(city)
        detail = self.getWeather(cityCode,city)
        # print (detail)
        return detail

if __name__ == "__main__":
    weather = SearchWeather()
    weather.predict_(city=input('请输入城市名称：'))



''''百度api'''
#
# import requests
# #引入python中内置的包
# import json
# while 1:
#     print('*************欢迎进入天气查询系统**************')
#     city=input('请输入您要查询的城市名称(按0退出)：')
#     if city=='0':
#         print('您已退出天气查询系统！')
#         break
#     else:
#         url='http://api.map.baidu.com/telematics/v3/weather?location=%s&output=json&ak=EA2udHiAv1Vwy1B6ktz9WupOmhB7szhC'%city
#         #使用requests发送请求，接受返回的结果
#         response=requests.get(url)
#         # print(type(response.text))
#         #使用loads函数，将json字符串转换为python的字典或列表
#         rs_dict=json.loads(response.text)
#         #取出error
#         error_code=rs_dict['error']
#         #如果取出的error为0，表示数据正常，否则没有查询到天气信息
#         if error_code==0:
#             #从字典中取出数据
#             results=rs_dict['results']
#             #根据索引取出城市天气信息字典
#             info_dict=results[0]
#             #根据字典的key 取出城市名称
#             city_name=info_dict['currentCity']
#             pm25=info_dict['pm25']
#             print('当前城市:%s pm值:%s'%(city_name,pm25))
#             #取出天气信息列表
#             weather_data=info_dict['weather_data']
#             #for循环取出每一天天气的小字典
#             for weather_dict in weather_data:
#                 #取出日期、天气、风级、温度
#                 date=weather_dict['date']
#                 weather=weather_dict['weather']
#                 wind=weather_dict['wind']
#                 temperature=weather_dict['temperature']
#                 print('%s %s %s %s'%(date,weather,wind,temperature))
#         else:
#             print('没有查询到天气信息！')



# import re, json
#
# import urllib.request
# def tianqi(url):
#     res1 = urllib.request.urlopen(url)
#     date = res1.read().decode("utf8")
#     pattern = re.compile(r'value="(.*?)" /')
#
#     res2 = re.findall(pattern, date)
#
#     return res2[1]
# # url_ = "http://www.weather.com.cn/weather1d/"
# url_ = "http://www.weather.com.cn/data/sk/"
# #输入城市中文
# city = input("请输入你要查询的城市：")
#
# #读取json文件
# f = open('city.json', 'rb')
#
# #使用json模块的load方法加载json数据，返回一个字典
# cities = json.load(f)
#
# #通过城市的中文获取城市代码
# city_id = cities.get(city)
# url = url_ + city_id + ".html"
# #网络请求，传入请求api+城市代码
# # response = requests.get(url + city)
# print(city,tianqi(url))
#
# # def max_seg(text):
#
#
# # def search_weather()