#coding:utf-8
import pandas as pd
from bool_config import BoolConfig
from bool_model import BoolSearch
import numpy as np
import jieba,os,re
from jieba.analyse import extract_tags

np.random.seed(10)
config = BoolConfig()


""" 一:清洗文本并划分数据集 """
def load_corpus(config):
    
    """ 读取数据 """
    print("\nLoading the dataset ... \n")
    corpus_xls = pd.ExcelFile(config.corpus_path)
    business_df = corpus_xls.parse("business_question")
    chatting_df = corpus_xls.parse("chatting_question")
    
    """ 进行文本清洗 """
    # business_df["question_seg"] = business_df["question"].apply(clean_text)
    # chatting_df["question_seg"] = chatting_df["question"].apply(clean_text)
    
    business_df.dropna(inplace=True)
    chatting_df.dropna(inplace=True)    
    
    """ to list """
    busi_ques = business_df["question"].tolist()
    chat_ques = chatting_df["question"].tolist()

    return busi_ques, chat_ques


""" 进行文本清洗 """
def clean_text(text):
    text = re.sub(
            "[\s+\-\|\!\/\[\]\{\}_,.$%^*(+\"\')]+|[:：+——()?【】《》“”！，。？、~@#￥%……&*（）]+", '',str(text).lower())
    
    if not text:
        return np.nan
    return text

'''加载停用词'''
def load_stop_words(stop_word_path):
    file = open(stop_word_path, 'r', encoding='utf-8')
    stop_words = file.readlines()
    stop_words = [stop_word.strip() for stop_word in stop_words]
    return stop_words
stop_words = load_stop_words(config.stopwords_path)

""" 用jieba分词 """
def clean_seg(text):
    text = clean_text(text)
    if type(text) is not str:
        return []
    else:
        words = jieba.lcut(text)
        # return ''.join([word for word in words if word not in stop_words])
        return ''.join([word for word in words]) # 闲聊不可加停用词


""" 二：bool取前5最相似句子 """
class BoolRecall(object):
    def __init__(self, qa_dict):
        self.qa_dict = qa_dict
        self.tokenizer = clean_seg
        self.bool_busi = BoolSearch(self.qa_dict, self.tokenizer)

    def recall(self, query, topn=10):
        
        """ 返回召回结果 """
        return self.bool_busi.get_topn(query, n=topn)
        


if __name__ == "__main__":
    
    model = BoolRecall()
    
    questions = ["我申请","社保业务","存单业务","查询外汇汇率","你家乡在哪里","好饿啊","你有男朋友吗","你觉得自己长得怎么样"]
    question_types = ["busi"] * 4 + ["chat"] * 4
    
    for question, type_ in zip(questions, question_types):
        print(model.recall(question,type_))    
