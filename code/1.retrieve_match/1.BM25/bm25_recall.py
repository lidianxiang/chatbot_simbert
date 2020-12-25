# coding:utf-8


'''
1、初始化IDF权重 idf:nd(包含该词的文档数） corpus_size:文档总数  avgdl：平均长度  doc_freqs：存储每个词及出现了该词的文档数量
                1）加载数据
                2）清洗分词
                3）得出IDF
2、gettopn 分词清洗  计算topN

'''
import sys
sys.path.append("../../")
from bm25_model import BM25kapi
from bm25_config import BmConfig
import pandas as pd
import numpy as np
import jieba, os, re
import time

start_time = time.time()

np.random.seed(10)
config = BmConfig()

""" 一:清洗文本并划分数据集 """


def load_corpus(base_list):
    busi_ques = []
    for item in base_list:
        busi_ques.append(item)
    return busi_ques


'''加载停用词'''


def load_stop_words(stop_word_path):
    file = open(stop_word_path, 'r', encoding='utf-8')
    stop_words = file.readlines()
    stop_words = [stop_word.strip() for stop_word in stop_words]
    return stop_words


stop_words = load_stop_words(config.stopwords_path)

""" 进行文本清洗 """


def clean_text(text):
    text = re.sub(
        "[\s+\-\|\!\/\[\]\{\}_,.$%^*(+\"\')]+|[:：+——()?【】《》“”！，。？、~@#￥%……&*（）]+", '', str(text).lower())

    if not text:
        return np.nan
    return text


""" 用jieba分词 """


def clean_seg(text):
    text = clean_text(text)
    if type(text) is not str:
        return []
    else:
        words = jieba.lcut(text)
        return ''.join([word for word in words if word not in stop_words])


""" 二：bm25取前5最相似句子 """


class Bm25Recall(object):
    def __init__(self, qa_df):
        self.qa_df = qa_df
        self.base_list = [item['question'] for item in qa_df]
        self.busi_ques = load_corpus(self.base_list)
        self.tokenizer = clean_seg
        self.bm25_busi = BM25kapi(self.busi_ques, self.tokenizer)
        # self.bm25_chat = BM25kapi(self.chat_ques, self.tokenizer)

    def recall(self, query, topn):

        return self.bm25_busi.get_top_n(query, self.qa_df, n=topn)




if __name__ == "__main__":
    a = [{'sim': '阿里巴巴开发商', 'res': 'alipay-开发商-阿里巴巴'}, {'sim': '阿里巴巴创立单位', 'res': '阿里学院-创立单位-阿里巴巴'}, {'sim': '阿里巴巴所属公司', 'res': '阿里妈妈-所属公司-阿里巴巴'}, {'sim': '阿里巴巴开发商', 'res': '千牛[阿里巴巴集团卖家工作台]-开发商-阿里巴巴'}, {'sim': '阿里巴巴单位', 'res': '诚信通-单位-阿里巴巴'}, {'sim': '阿里巴巴公司', 'res': '贸易通-公司-阿里巴巴'}, {'sim': '阿里巴巴企业', 'res': 'B2C-企业-阿里巴巴'}, {'sim': '阿里巴巴开发商', 'res': '淘宝助理-开发商-阿里巴巴'}]
    model = Bm25Recall(a)  # 初始化  求出权重

    print(model.recall("阿里巴巴创始人", 15))
