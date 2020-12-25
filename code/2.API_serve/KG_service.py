#coding:utf-8
from sanic import Sanic
from sanic import response
import json
import time
from sanic.exceptions import NotFound
from service_helper import Server

server = Server()

""" 定义 ip和端口号 """
app = Sanic(__name__)
ip, port = "127.0.0.1", 9010
""" 路由 (ExmaServer) 错误时，返回错误信息 """
@app.exception(NotFound)
async def url_404(request, excep):
    return response.json({"Error":excep})

""" 定义路由（ExmaServer）和请求方式（POST) """
@app.route('/QA',methods=['POST'])
async def model_server(request):
    try:
        request_json = request.body
        input_json = json.loads(request_json.decode('utf-8'))
        start_time = time.time()
        result = server.get_result(input_json)
        print('耗时：', time.time() - start_time)
    except Exception as e:
        result = {"code": 400, "message": "预测失败", "Error": e}
    return response.json(result)


if __name__ == '__main__':
    app.run(host=ip,port=port,debug=True)