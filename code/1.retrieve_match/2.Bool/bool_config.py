#coding:utf-8
import numpy as np
import os,pathlib

root = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent.parent


class BoolConfig(object):
    def __init__(self):
        self.stopwords_path = os.path.join(root, "data", "stopwords", "哈工大停用词表.txt")
