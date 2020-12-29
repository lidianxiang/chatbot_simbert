# -*- coding:utf-8 -*-
import re,os,time
from collections import defaultdict
from jieba.analyse import extract_tags
import numpy as np
from itertools import combinations


class BoolSearch:
    def __init__(self, documents,tokenizer=None):
        self.qa_dict = documents
        self.documents = [item['question'] for item in documents]
        self.tokenizer = tokenizer
        self.dic_word_doc = defaultdict(list) # word2docid  每个词对应的是哪个doc的  类似bert的segment
        self.doc_map = {} # id2doc
        self.dic_word_id = defaultdict(int)
        self.matrix = self._build_matrix()
                
                
    """ 得到倒排表 """
    def _build_rev_dic(self):
        
        # for doc_id, doc in enumerate(self.documents):
        for doc_id, item_ in enumerate(self.qa_dict):
            self.doc_map[doc_id] = item_
            
            words = self.tokenizer(item_["question"])
            for word in words:
                self.dic_word_doc[word].append(doc_id)
      
                
    """ 得到布尔矩阵 """           
    def _build_matrix(self):
        
        self._build_rev_dic()
        
        """ 构造布尔矩阵 """
        word_num = len(self.dic_word_doc)
        doc_num = len(self.documents)
        matrix = np.zeros((word_num,doc_num)).astype(np.int16) # 构建布尔矩阵
               
        for word_id,(word,doc_ids) in enumerate(self.dic_word_doc.items()):
            
            for doc_id in self.doc_map: # 该词在该doc中有出现 则设置该位置为1
                if doc_id in doc_ids:
                    matrix[word_id,doc_id] = 1 
            
            """ 构建词表 """ 
            self.dic_word_id[word] = word_id
            
        return matrix
    
    """ 取出所有关键词的布尔向量 """
    def _get_vector_inter(self,word_ids):
        
        """ 取取布尔向量 """
        vectors = self.matrix[word_ids]
        
        """ 求交集 """
        vector_inter = np.where(vectors.sum(axis=0) == len(word_ids),1,0) # 满足条件(condition)，输出x，不满足输出y
        
        return vector_inter
            
    """ 取出包含文档的布尔向量 """
    def _get_vector(self,word_ids,topn=3):
        
        """ 返回 [] """
        if topn == 0:
            return []
        
        """ 如果关键词数量小于3，那么把topn设为关键词数量 如果满了就只有一种排列组合"""
        topn = len(word_ids[:topn])
        
        """ 对关键词做组合 """
        comb_ids = list(combinations(range(len(word_ids)),topn)) # [(0, 1)] combinations排列组合
        for ids in comb_ids:
            word_ids_f = [word_ids[idx] for idx in ids]
            vector_inter = self._get_vector_inter(word_ids_f)
            
            """ 取到文档，则返回结果 """
            if max(vector_inter) == 1:
                return vector_inter
        
        return self._get_vector(word_ids, topn-1) # 重复多次
                
                
    """ 取出前topn条问题 """
    def get_topn(self,query,n=10):
        
        """ 得到关键词 """
        words = self.tokenizer(str(query))
        
        """ 过滤不在词表中的词 分字"""
        word_ids = [self.dic_word_id[word] for word in words if word in self.dic_word_id] 
        
        if not word_ids:
            return []
        
        """ 取出布尔向量 """
        vector = self._get_vector(word_ids)
        
        if len(vector) == 0:
            return []
        '''取出所有词都存在的句子 应该按出现最多的方式来取'''
        docs = [self.doc_map[i] for i,idx in enumerate(vector) if idx==1]
        return docs[:n]