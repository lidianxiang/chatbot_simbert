# coding:utf-8
# https://mp.weixin.qq.com/s/0hZX11nogU7Opbr3Ahkp3g
from wxpy import *
from server import chat_service

import random, re

""" 1: 第一次运行，需要扫码。把cache_path设为True，生成微信登录的缓存文件"""
bot = Bot(cache_path=True)  # 开启缓存后可在短时间内避免重复扫码，缓存失效时会重新要求登陆。
# bot = Bot()
""" 2: 下一次运行，就直接加载缓存文件，不需要扫码了"""
# bot = Bot(cache_path="wxpy.pkl")
""" 3: 可以设置为对特定某个人回复"""
# my_friend = bot.friends().search("Katherine 石萌多吃会变丑")[0]
# print(my_friend)
""" 4: 只对特定某个人回复"""
# @bot.register(my_friend)
import pandas as pd

all_df = pd.DataFrame()


@bot.register(chats=[Friend])
def auto_response(msg):
    # f = Friend
    # print(f.remark_name)
    # print('msh:' + msg)

    print("[接收1]:" + msg.text)
    print("[格式]:" + str(msg.type))
    print('[名字]：' + msg.chat.name)
    send_name = msg.chat.name

    if msg.type == "Picture":
        return "卓师叔不会斗图也不会发表情包哦！[奸笑]\n\n"

    if msg.type == "Recording":
        return "卓师叔没带耳机呢[皱眉]打字行吗？\n\n"

    if msg.type == "Video":
        return "你发idol的MV我才会看哦！[吃瓜]\n\n"

    query = str(msg).split(':')[1]
    query = re.sub("\(Text\)", "", query).strip()
    print("[接收2]:" + query)
    if query in ["[捂脸]", "[皱眉]", "[憨笑]", "[OK]", "[奸笑]", "[旺柴]", "[敲打]", "[擦汗]", "[微笑]", "[撇嘴]", "[发呆]", "[流泪]", "[尴尬]",
                 "[偷笑]", "[奋斗]", "[抠鼻]", "[坏笑]", "[吃瓜]", "[呲牙]", "[耶]", "[Emm]", "[社会社会]", "[嘿哈]"]:
        return random.choice(["[捂脸]", "[皱眉]", "[奸笑]", "[旺柴]", "[微笑]", "[偷笑]", "[坏笑]", "[吃瓜]", "[社会社会]"])

    if len(query) <= 1 or query in ["Hi", "你好", "您好", "嗨", "hello", "Hello", "1", " ", "哈哈", "哈罗", "哈啰", "", "", "", "",
                                    "", "", "", "", "", "", "", "", "", "", ""]:
        return "您好,卓师叔在呢，有什么可以为你服务？"

    if query in ["浦发信用卡", "浦发银行", "很高心认识你", "卓"]:
        return "您好,很高心为你服务"

    if query in ["。。。", "...", "......", "。。。。。。", "？", "？？？"]:
        return "无语了是吧？我比你更无语呢。"

    ret = chat_service(query, send_name, 9010)
    if ret == "电脑":
        ret = "卓师叔不知道该说啥了[皱眉]"
    print("[发送]:" + str(ret))

    return ret


embed()
