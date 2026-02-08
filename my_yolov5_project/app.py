import json
import time
import uuid
import itertools
import pymysql
from pymysql import Error
from threading import Event
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
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
socketio.init_app(app)

# 建立 Redis 连接
redis_client = redis.Redis(host='localhost', port=6379, db=0)

detection_counter = itertools.count(1)

stop_event = Event()

# mysql
mysql_config = {
    'host': 'localhost',
    'database': 'xdb',
    'user': 'root',
    'password': '123456',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 全局变量
detection_buffer = []


# mysql数据库连接
def create_mysql_connection():
    try:
        connection = pymysql.connect(**mysql_config)
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
    return None


# 将数据插入到mysql数据库
def insert_detections_to_mysql(detections):
    connection = create_mysql_connection()
    if connection is None:
        print("Failed to connect to MySQL")
        return
    try:
        with connection.cursor() as cursor:
            query = """INSERT INTO detections 
                       (session_id, timestamp, class_name, source, confidence, user_id) 
                       VALUES (%s, %s, %s, %s, %s, %s)"""
            cursor.executemany(query, detections)
        connection.commit()
        print(f"{cursor.rowcount} records inserted successfully into detections table")
    except Error as e:
        print(f"Failed to insert records into MySQL table: {e}")
    finally:
        connection.close()


def get_last_session_id():
    connection = create_mysql_connection()
    if connection is None:
        print("Failed to connect to MySQL")
        return None
    try:
        with connection.cursor() as cursor:
            query = "SELECT session_id FROM detections ORDER BY id DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchone()
            if result:
                last_id = result['session_id']
                # 假设格式为 'det_000001'，我们提取数字部分
                return int(last_id.split('_')[1])
            else:
                return 0  # 如果没有记录，从0开始
    except Error as e:
        print(f"Error querying last session ID: {e}")
        return 0
    finally:
        connection.close()


# 将检测数据添加到 Redis
def add_detection_to_redis(detection_data):
    detection_id = next(detection_counter)
    detection = (
        f"det_{detection_id:06d}",
        datetime.now().isoformat(),
        detection_data['class_name'],
        detection_data['source'],
        detection_data['confidence'],
        detection_data['user_id']
    )
    # 添加到Redis
    detection_json = json.dumps({
        'session_id': detection[0],
        'timestamp': detection[1],
        'class_name': detection[2],
        'source': detection[3],
        'confidence': detection[4],
        'user_id': detection[5]
    })
    redis_client.lpush('detections', detection_json)
    socketio.emit('detection_result', json.loads(detection_json))

    # 添加到缓冲区
    detection_buffer.append(detection)
    # print(f"Added detection to buffer. Buffer size: {len(detection_buffer)}")
    # print(detection_json)
    # 如果缓冲区达到20条，则存入MySQL
    if len(detection_buffer) >= 20:
        # print("Buffer reached 20 items. Inserting into MySQL...")
        insert_detections_to_mysql(detection_buffer)
        detection_buffer.clear()  # 清空缓冲区
        # print("Buffer cleared after MySQL insertion.")
        # 发送 WebSocket 事件


# 启动检测
@app.route('/video_feed')
def video_feed():
    global detection_active
    session_id = str(uuid.uuid4())

    def generate():
        while True:
            yield from run(session_id=session_id, user_id=user_id, add_detection_to_redis=add_detection_to_redis,
                           stop_event=stop_event)

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


# 开始检测
@socketio.on('start_detection')
def handle_start_detection(data):
    stop_event.clear()  # 清除停止事件
    # 清空 Redis 中的检测数据
    redis_client.delete('detections')
    print("Cleared previous detections from Redis")

    # 重置检测计数器
    global detection_counter
    detection_counter = itertools.count(1)

    # 获取最后的 session_id 并设置新的 detection_counter
    last_id = get_last_session_id()
    detection_counter = itertools.count(last_id + 1)

    # 清空检测缓冲区
    global detection_buffer
    detection_buffer.clear()


# 停止检测
@socketio.on('stop_detection')
def handle_stop_detection(data):
    stop_event.set()  # 设置停止事件


# WebSocket连接事件
@socketio.on('connect')
def handle_connect():
    global user_id
    user_id = request.args.get('userId')
    print(f"User {user_id} connected")
    return user_id


# WebSocket断开连接事件
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app, debug=True, host="localhost", port='5000', allow_unsafe_werkzeug=True)
