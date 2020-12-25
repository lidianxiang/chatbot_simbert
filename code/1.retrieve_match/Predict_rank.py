# coding:utf-8
import sys, os, pathlib
import numpy as np
import pandas as pd
from functools import reduce

root = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent
print(root)
bm25_root = os.path.join(root, 'code/1.retrieve_match/1.BM25')
bool_root = os.path.join(root, 'code/1.retrieve_match/2.Bool')
simbert_root = os.path.join(root, 'code/1.retrieve_match/3.simbert_match')
config_root = os.path.join(root, 'code/1.retrieve_match/4.model_config')

sys.path.extend([bm25_root, bool_root, simbert_root, config_root])

from bm25_recall import Bm25Recall
from bool_recall import BoolRecall
from retireval_bunny import retireval_sim
from model_config import Config
cf = Config()


class Rank(object):
    def __init__(self, qa_dict):
        self.bm25_pred = Bm25Recall(qa_dict).recall
        self.bool_pred = BoolRecall(qa_dict).recall

    def get_answer(self, query, topn=10, threshold=0.5):
        '''
        :param query: 问句
        :param topn: 粗排时需要返回的topn
        :param threshold: 精排的阈值
        :return:
        '''
        '''一、粗排：BM25和Bool检索一起用'''
        # bm25粗排 会导致常用词，常用聊天（频率高的字词）匹配不上。
        bm25_qa = self.bm25_pred(query, topn)

        # bool检索粗排  中和掉bm25的问题
        bool_qa = self.bool_pred(query, topn)

        # 合并bm25和bool的结果
        match_qa = bm25_qa[:int(topn/2)] + bool_qa[:int(topn/2)]
        match_qa = reduce(lambda x,y:x if y in x else x + [y], [[], ] + match_qa) # 去重

        '''二、精排：用simbert做句子相似性匹配'''
        sim_pred = retireval_sim(match_qa)
        sim_qa = sim_pred.most_similar(query)

        '''三、输出结果'''
        topn_one = sim_qa[0]
        topn_recall_sort = sim_qa[1:6]  # 切片就算没有也不会报错
        if topn_one["sim_rate"] < threshold:
            topn_recall_sort = []
            topn_one = {'question': '无法解答', 'answer': cf.cannot_ans, 'sim_rate': 0.0}
            return topn_one, topn_recall_sort

        return topn_one, topn_recall_sort  # 返回字典


def match(text):
    text = text.lower()
    if len(text) <= 1 or text in ["hi", "你好", "您好", "嗨", "hello", "Hello", "1", " ", "哈哈", "哈罗", "哈啰", "哈喽", "很高心认识你", "你是谁", "是谁", "您是谁", "。。。", "...", "......", "。。。。。。","哈哈哈","??", "？？？"]:
        return cf.hello_ans


if __name__ == "__main__":
    import json
    data_path = os.path.join(root,'data/qa_corpus.xlsx')

    questions = ["你叫什么", "怎么回事", "手机上不了网"]
    qa_df = pd.read_excel(data_path)
    qa_df["question"] = qa_df["question"].apply(str)
    qa_df["answer"] = qa_df["answer"].apply(str)
    qa_dict = qa_df.to_dict(orient="records")
    ranker = Rank(qa_dict)

    for query in questions:
        match_answer = ranker.get_answer(query)

        print("\nThe question matched is %s \n\n " % str(match_answer))
