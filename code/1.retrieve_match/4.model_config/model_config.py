# coding:utf-8
import sys, os, pathlib
from functools import reduce
import numpy as np

root = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent
print(root)


class Config:

    def __init__(self):
        self.message_dic = message_dic = {'000': '成功',
                                          '100': '模型预测失败',
                                          '300': '请求格式错误',
                                          '400': '没有输入内容'}  # 000 成功  100 无答案 预测失败

        self.hello_ans = "您好，卓师叔在呢，有什么可以为您服务？"
        self.cannot_ans = "不好意思，卓师叔还在学习，暂时理解不了您说的问题，您可以留言咨询。"

        # 天气相关
        self.weather_path = os.path.join(root, 'code/1.retrieve_match/5.weather_search/city.json')
        self.weather_match_q = ["今天天气怎么样", "天气怎么样", "明天天气怎么样", "明天会下雨吗", "今天是什么天气", "今天天气咋样"]

        self.duplicate_txt = ["咦，怎么又是这句呀", "好好说话行不行呀？", "不想和你说话了耶，您再见吧", "我回答过了哦", "我们换个话题继续聊吧", "换个话题再来问我吧", "怎么老是一句话", "你刚刚问过这个问题了", "好烦呀，我不要跟你聊天了"]
        self.duplicate_picture = {"2": ["你已经发了两张图啦，我看不懂的"],
                                  "3": ["还是图片更有趣", "看来你很喜欢发图嘛！", "聊的好好的突然发图，防不胜防", "冷不防，又是一张", "看来你很喜欢发图嘛！", "观图不语真君子", "你给我发图，我也不懂", "还是坦白说吧，我看不懂图片", "是真的不懂，用文字描述给我吧", "一直发图片，我都不知道该说什么。", "明知我看不懂，还要逗我玩", "好好唠嗑，不要抛图片了", "这是一言不合就发图的节奏", "还在发，其实我看不懂的", "我已经说过了，看不懂", "我已经懵了，都是图片", "咱们能不能不发图片了？", "我是聊天机器人，不是图像识别机器人", "图图图，又是图片。。。"]}

    def norma_ans(self, query, bm25_pred, bool_pred, retireval_sim, topn):
        '''一、粗排：BM25和Bool检索一起用'''
        # bm25粗排 会导致常用词，常用聊天（频率高的字词）匹配不上。
        bm25_qa = bm25_pred(query, topn)
        print("bm25 匹配到的问题：", bm25_qa)

        # bool检索粗排  中和掉bm25的问题
        bool_qa = bool_pred(query, topn)
        print("bool 匹配到的问题：", bool_qa)

        # 合并bm25和bool的结果
        match_qa = bm25_qa[:int(topn / 2)] + bool_qa[:int(topn / 2)]
        match_qa = reduce(lambda x, y: x if y in x else x + [y], [[], ] + match_qa)  # 去重

        '''二、精排：用simbert做句子相似性匹配'''
        sim_pred = retireval_sim(match_qa)
        sim_qa = sim_pred.most_similar(query)
        '''三、输出结果'''
        topn_one = sim_qa[0]
        topn_recall_sort = sim_qa[1:6]  # 切片就算没有也不会报错

        return topn_one, topn_recall_sort

    # 多轮查询天气
    def multi_weather(self, query, seg_model, weather_model, flag):
        city = []
        match_seg = seg_model(query)

        for k, v in match_seg:
            if v == "城市":
                city.append(k)
        # 第一次问，且没有提到城市
        if city == [] and flag == "normal":
            res = "请问您想查询哪个城市？"
            flag = "weather"
        elif len(city) == 1:
            res = weather_model(city=city[0])
            flag = "normal"
        elif len(city) > 1:
            res = "请问您具体想查询的哪个城市？{}".format('？'.join(i for i in city))
            flag = "weather"
        topn_recall_sort = []
        topn_one = {'question': '查询天气', 'answer': res, 'sim_rate': 0.0}
        return topn_one, topn_recall_sort, flag

    def duplicate_response(self, duplicate_q, type):

        if type == 'Picture':
            if len(duplicate_q) == 2:
                res = np.random.choice(self.duplicate_picture["2"])
                topn_one = {'question': '重复图片', 'answer': res, 'sim_rate': 0.0}
                return topn_one, []
            elif len(duplicate_q) >= 3:
                res = np.random.choice(self.duplicate_picture["3"])
                topn_one = {'question': '重复图片', 'answer': res, 'sim_rate': 0.0}
                return topn_one, []
        else:
            res = np.random.choice(self.duplicate_txt)
            topn_one = {'question': '重复文字', 'answer': res, 'sim_rate': 0.0}
            return topn_one, []

