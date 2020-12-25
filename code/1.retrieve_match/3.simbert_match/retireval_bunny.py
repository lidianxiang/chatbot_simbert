# coding:utf-8
import numpy as np
import json
import tensorflow as tf
from collections import Counter
from bert4keras.layers import Loss
from bert4keras.backend import keras, K
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam, extend_with_weight_decay
from bert4keras.tokenizers import Tokenizer, load_vocab
from bert4keras.snippets import sequence_padding
from bert4keras.snippets import open
from keras.models import Model
import sys, pathlib, os

sys.path.append("..")
root = pathlib.Path(os.path.abspath(__file__)).parent
maxlen = 64

# bert配置
cf_root = os.path.join(root, "config/chinese_simbert_L-12_H-768_A-12")
config_path = os.path.join(cf_root, "bert_config.json")
checkpoint_path = os.path.join(cf_root, "bert_model.ckpt")
dict_path = os.path.join(cf_root, "vocab.txt")

# 加载并精简词表，建立分词器
token_dict, keep_tokens = load_vocab(
    dict_path=dict_path,
    simplified=True,
    startswith=['[PAD]', '[UNK]', '[CLS]', '[SEP]'],
)
# 建立分词器
tokenizer = Tokenizer(token_dict, do_lower_case=True)  # 建立分词器

config = tf.ConfigProto(intra_op_parallelism_threads=1,allow_soft_placement=True)
session = tf.Session(config=config)
keras.backend.set_session(session)
# 建立加载模型
bert = build_transformer_model(
    config_path,
    checkpoint_path,
    with_pool='linear',
    application='unilm',
    keep_tokens=keep_tokens,
    return_keras_model=False,
)

class TotalLoss(Loss):
    """loss分两部分，一是seq2seq的交叉熵，二是相似度的交叉熵。
    """
    def compute_loss(self, inputs, mask=None):
        loss1 = self.compute_loss_of_seq2seq(inputs, mask)
        loss2 = self.compute_loss_of_similarity(inputs, mask)
        self.add_metric(loss1, name='seq2seq_loss')
        self.add_metric(loss2, name='similarity_loss')
        return loss1 + loss2

    def compute_loss_of_seq2seq(self, inputs, mask=None): # 计算生成中的loss
        y_true, y_mask, _, y_pred = inputs # y_pred：(?,?,13584)
        y_true = y_true[:, 1:]  # 目标token_ids 可以看原理知道预测的内容是哪些
        y_mask = y_mask[:, 1:]  # segment_ids，刚好指示了要预测的部分，也就是说只有第二句话，也就是为1的要预测  cls不取
        y_pred = y_pred[:, :-1]  # 预测序列，错开一位
        loss = K.sparse_categorical_crossentropy(y_true, y_pred)
        loss = K.sum(loss * y_mask) / K.sum(y_mask) # ()
        return loss

    def compute_loss_of_similarity(self, inputs, mask=None):
        _, _, y_pred, _ = inputs
        y_true = self.get_labels_of_similarity(y_pred)  # 构建标签  (btz,btz) 左右两个btz互为true
        y_pred = K.l2_normalize(y_pred, axis=1)  # 句向量归一化 (?, 768)
        similarities = K.dot(y_pred, K.transpose(y_pred))  # 相似度矩阵 (btz,btz)
        similarities = similarities - K.eye(K.shape(y_pred)[0]) * 1e12  # 排除对角线，因为对角线的是自己跟自己比 (btz,btz) 对角线上的值会变得无穷小
        similarities = similarities * 30  # scale (btz,btz)
        loss = K.categorical_crossentropy(
            y_true, similarities, from_logits=True
        ) # (?,)  由此可以计算一个btz内的句子相似度
        return loss

    def get_labels_of_similarity(self, y_pred):
        idxs = K.arange(0, K.shape(y_pred)[0]) # 0到btz (btz,)
        idxs_1 = idxs[None, :] # (1, btz)
        idxs_2 = (idxs + 1 - idxs % 2 * 2)[:, None] # (?,1)
        labels = K.equal(idxs_1, idxs_2) # (btz, btz) 左右摇，相邻的两个btz是代表着相似的（generator中设置了前后颠倒）
        '''
        所以btz中，[0]是在第二个位置为True，[1]是在第一个位置为True， [2]是在第四个位置为True，[3]是在第三个位置为True。。。
        '''
        labels = K.cast(labels, K.floatx()) # 从true和false转成0 1
        '''
        [
            [0, 1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0],
            ...
            [0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 1, 0]]
        '''
        return labels # (btz, btz)
encoder = keras.models.Model(bert.model.inputs, bert.model.outputs[0]) # 用于相似 Tensor("Pooler-Dense/BiasAdd:0", shape=(?, 768), dtype=float32)
seq2seq = keras.models.Model(bert.model.inputs, bert.model.outputs[1]) # 用于生成 Tensor("MLM-Activation/truediv:0", shape=(?, ?, 13584), dtype=float32)

outputs = TotalLoss([2, 3])(bert.model.inputs + bert.model.outputs) # 每一个里面都是一个list，都有两个东西
model = keras.models.Model(bert.model.inputs, outputs)
AdamW = extend_with_weight_decay(Adam, 'AdamW')
optimizer = AdamW(learning_rate=2e-6, weight_decay_rate=0.01)
model.compile(optimizer=optimizer)
# model.load_weights(model_path)

def get_vecs(qa_df):
    # print("======================================================")
    # print("qa_df", qa_df)
    token_ids = []
    for d in qa_df:
        token_id = tokenizer.encode(d['question'], max_length=maxlen)[0]
        token_ids.append(token_id)

    token_ids = sequence_padding(token_ids)
    with session.as_default():
        with session.graph.as_default():
            q_vecs = encoder.predict([token_ids, np.zeros_like(token_ids)], verbose=True)  # (185, 782)
            q_vecs = q_vecs / (q_vecs ** 2).sum(axis=-1, keepdims=True) ** 0.5  # (185, 782)
    return q_vecs

class retireval_sim:

    def __init__(self, qa_df):
        self.qa_df = qa_df
        self.q_vecs = get_vecs(qa_df)

    def most_similar(self, text, topn=10):
        # print("text", text)
        with session.as_default():
            with session.graph.as_default():
                q_token_id, segment_id = tokenizer.encode(text, max_length=maxlen)
                # print("q_token_id", q_token_id)
                q_vec = encoder.predict([[q_token_id], [segment_id]])[0]
                q_vec /= (q_vec ** 2).sum() ** 0.5
                # print("query_vecs", q_vec)
                sims = np.dot(self.q_vecs, q_vec)
                # print("sims", sims)
                res = [{"question": self.qa_df[i]['question'], "answer": self.qa_df[i]['answer'], "sim_rate": sims[i]} for i in sims.argsort()[::-1][:topn]]
        return res

if __name__ == '__main__':
    import time
    # recall = retireval_sim(train_data)
    # start_time = time.time()
    # res = recall.most_similar('账号解锁')
    # print(res)
    # print("--------------------------------------------------------------------------------------------------------------------------------------------------------")
    # print("top1:", res[0])
    # print("预测耗时：", time.time() - start_time)
