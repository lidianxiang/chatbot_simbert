# coding:utf-8
class Config:

    def __init__(self):
        self.message_dic = message_dic = {'000': '成功',
                                           '100': '模型预测失败',
                                           '300': '请求格式错误',
                                           '400': '没有输入内容'} # 000 成功  100 无答案 预测失败

        self.hello_ans = "您好，卓师叔在呢，有什么可以为您服务？"
        self.cannot_ans = "不好意思，卓师叔还在学习，暂时理解不了您说的问题，您可以留言咨询。"