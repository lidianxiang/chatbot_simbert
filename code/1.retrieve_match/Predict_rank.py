# coding:utf-8
import sys, os, pathlib
import numpy as np
import pandas as pd
from collections import deque
import json

root = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent
print(root)
bm25_root = os.path.join(root, 'code/1.retrieve_match/1.BM25')
bool_root = os.path.join(root, 'code/1.retrieve_match/2.Bool')
simbert_root = os.path.join(root, 'code/1.retrieve_match/3.simbert_match')
config_root = os.path.join(root, 'code/1.retrieve_match/4.model_config')
weather_root = os.path.join(root, 'code/1.retrieve_match/5.weather_search')
max_seg_root = os.path.join(root, 'code/1.retrieve_match/6.max_segment')

sys.path.extend([bm25_root, bool_root, simbert_root, config_root, weather_root, max_seg_root])

from bm25_recall import Bm25Recall
from bool_recall import BoolRecall
from retireval_bunny import retireval_sim
from model_config import Config
from weather import SearchWeather
from max_seg import PsegMax

cf = Config()


class Rank(object):
    def __init__(self, qa_dict):
        self.bm25_pred = Bm25Recall(qa_dict).recall
        self.bool_pred = BoolRecall(qa_dict).recall
        self.weather_data = json.load(open(cf.weather_path, 'rb'))
        self.weather = SearchWeather(self.weather_data).predict_
        self.max_seg = PsegMax(self.weather_data).max_biward_seg

        # 意图标签
        self.flag = "normal"
        # 初次次调用，初始化一下，保证至少有一个值在
        self.duplicate_q = ['start']

    def get_answer(self, query, type=None, topn=10, threshold=0.5):
        '''
        :param query: 问句
        :param topn: 粗排时需要返回的topn
        :param threshold: 精排的阈值
        :return:
        '''
        '''判断是否重复多次一样问题，text情况下，第三次开始返回重复的'''
        if query == self.duplicate_q[-1]:
            self.duplicate_q.append(query)
            topn_one, topn_recall_sort = cf.duplicate_response(self.duplicate_q, type)
            return topn_one, topn_recall_sort
        else:
            self.duplicate_q = []
            self.duplicate_q.append(query)


        '''用flag做判断，初始或者常规的都是normal'''
        if self.flag == "normal":
            topn_one, topn_recall_sort = cf.norma_ans(query, self.bm25_pred, self.bool_pred, retireval_sim, topn)


        '''判断是否查询天气'''
        if (self.flag == "weather") or (topn_one['question'] in cf.weather_match_q):
            topn_one, topn_recall_sort, self.flag = cf.multi_weather(query, self.max_seg, self.weather, self.flag)
            return topn_one, topn_recall_sort


        '''无法解答的情况'''
        if topn_one["sim_rate"] < threshold:
            topn_recall_sort = []
            topn_one = {'question': '无法解答', 'answer': cf.cannot_ans, 'sim_rate': 0.0}
            return topn_one, topn_recall_sort

        return topn_one, topn_recall_sort  # 返回字典


def match(text):
    text = text.lower()
    if len(text) <= 1 or text in ["hi", "你好", "您好", "嗨", "hello", "Hello", "1", " ", "哈哈", "哈罗", "哈啰", "哈喽", "很高心认识你",
                                  "你是谁", "是谁", "您是谁", "。。。", "...", "......", "。。。。。。", "哈哈哈", "??", "？？？"]:
        return cf.hello_ans


if __name__ == "__main__":

    data_path = os.path.join(root, 'data/qa_corpus.xlsx')
    questions = ["天气怎么样", "莆田", "你叫什么名字", "你叫什么名字", "你叫什么名字", "你叫什么名字", "你叫什么名字", "你叫什么名字"]
    qa_df = pd.read_excel(data_path)
    qa_df["question"] = qa_df["question"].apply(str)
    qa_df["answer"] = qa_df["answer"].apply(str)
    qa_dict = qa_df.to_dict(orient="records")
    ranker = Rank(qa_dict)

    for query in questions:
        match_answer = ranker.get_answer(query)

        print("\nThe question matched is %s \n\n " % str(match_answer))
