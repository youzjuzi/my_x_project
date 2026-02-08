import json
import uuid

from flask import Flask, render_template, Response, request
import os, sys, redis
from pathlib import Path
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime

FILE = Path(__file__).absolute()
sys.path.append(FILE.parents[0].as_posix())  # add yolov5/ to path
from detect import run

app = Flask(__name__)
CORS(app)  # 允许所有域名访问
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # 允许所有来源
socketio.init_app(app)

# 建立 Redis 连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def add_detection_to_redis(detection_data):
    detection = {
        'session_id': detection_data['session_id'],
        'timestamp': datetime.now().isoformat(),
        'class_name': detection_data['class_name'],
        'source': detection_data['source'],
        'confidence': detection_data['confidence'],
        'user_id': detection_data['user_id']
    }
    # 将检测数据序列化为 JSON 字符串
    detection_json = json.dumps(detection)

    # 使用 LPUSH 命令将数据添加到 Redis 列表
    redis_client.lpush('detections', detection_json)


# @app.route('/video_feed')
# def video_feed():
#     return Response(run(), mimetype='multipart/x-mixed-replace; boundary=frame')


@socketio.on('connect')
def handle_connect():
    user_id = request.args.get('userId')
    print(f"User {user_id} connected")
    return user_id


@socketio.on('start_detection')
def handle_start_detection(data):
    user_id = data.get('userId')
    session_id = str(uuid.uuid4())  # 生成唯一的会话 ID

    def detection_callback(detections):
        for detection in detections:
            detection_data = {
                'session_id': session_id,
                'class_name': detection['class_name'],
                'source': 'webcam',
                'confidence': detection['confidence'],
                'user_id': user_id
            }
            add_detection_to_redis(detection_data)
            socketio.emit('detection_result', detection_data, room=request.sid)

    # 启动检测
    run(callback=detection_callback)


# WebSocket断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


# WebSocket消息事件
@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)
    emit('response', {'data': data})


if __name__ == '__main__':
    app.run(debug=True)
    # socketio.run(app, debug=True,host="localhost",port='5000')
