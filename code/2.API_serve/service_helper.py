# coding:utf-8
import sys, pathlib, os
root = pathlib.Path(os.path.abspath(__file__)).parent.parent.parent
rank_path = os.path.join(root, 'code/1.retrieve_match')
data_path = os.path.join(root,'data/qa_corpus.xlsx')
sys.path.append(rank_path)
from Predict_rank import Rank
import pandas as pd

""" 服务被调用时的情况 """
message_dic = {'200': '正常',
               '300': '请求格式错误',
               '400': '模型预测失败'}

qa_df = pd.read_excel(data_path)
qa_df["question"] = qa_df["question"].apply(str)
qa_df["answer"] = qa_df["answer"].apply(str)
qa_dict = qa_df.to_dict(orient="records")


class Server:
    def __init__(self):
        """
        把模型的预测函数初始化,
        """
        self.predict = Rank(qa_dict).get_answer

    """ 把json格式的请求数据，解析出来 """
    def parse(self, app_data):
        request_id = app_data["request_id"]
        text = app_data["query"]
        return request_id, text

    """ 得到服务的调用结果，包括模型结果和服务的情况 """

    def get_result(self, data):
        code = '200'
        try:
            request_id, text = self.parse(data)
        except Exception as e:
            print('error info : {}'.format(e))
            code = '300'
            request_id = "None"
        try:
            if code == '200':
                # answer, ques_type, _ = self.predict(text)
                answer, topn_recall_sort = self.predict(text)

            elif code == '300':
                answer = '亲,对不起,卓师叔目前还理解不了你的问题'
                ques_type = "None"
        except Exception as e:
            print('error info : {}'.format(e))
            answer = '亲,对不起,卓师叔目前还理解不了你的问题'
            ques_type = 'None'
            code = '400'

        result = {'answer': answer["answer"], 'code': code,
                  'message': message_dic[code], 'request_id': request_id}

        return result


if __name__ == "__main__":
    server = Server()
    data = {"request_id": "ExamServer",
            "query": "你会说话嘛"}
    print("\n The result is ", server.get_result(data))
