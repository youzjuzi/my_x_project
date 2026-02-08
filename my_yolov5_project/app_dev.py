from flask import Flask, render_template, Response
import os, sys
from pathlib import Path
from flask_socketio import SocketIO, emit
from flask_cors import CORS

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path
from detect import run

app = Flask(__name__)
CORS(app)  # 允许所有域名访问
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许所有来源
socketio.init_app(app)


@app.route("/")
def hello_world():
    return render_template('index.html')


# @app.route('/video_feed')
# def video_feed():
#     return Response(run(), mimetype='multipart/x-mixed-replace; boundary=frame')


# WebSocket连接事件
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('server_response', {'data': 'Connected'})


# WebSocket断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# WebSocket消息事件
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    emit('response', {'data': data})


@socketio.on('test', namespace='api')  # 监听前端发回的包头 test ,应用命名空间为 api
def test():  # 此处可添加变量，接收从前端发回来的信息
    print('触发test函数')
    socketio.emit('api', {'data':'test_OK'}, namespace='api')  # 此处 api 对应前端 sockets 的 api


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True, host="localhost", port='5000', allow_unsafe_werkzeug=True)
