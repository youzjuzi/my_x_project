import redis
import json
from datetime import datetime

#建立redis连接
redis_client = redis.Redis(host='localhost',port=6379,db=0)

def add_detection_to_redis(detection_data):
    """
       将检测数据添加到Redis

       :param detection_data: 包含检测信息的字典
       """
    # 如果没有提供用户ID，则尝试获取当前用户ID
    detection = {
        'session_id': detection_data['session_id'], #唯一标识
        'timestamp': datetime.now().isoformat(),    #时间
        'class_name': detection_data['class_name'], #识别名字
        'source': detection_data['source'],         #来源
        'confidence': detection_data['confidence'], #精度
        'user_id': detection_data['user_id']        #用户id
    }

    # 将检测数据序列化为JSON字符串
    detection_json = json.dumps(detection)

    # 使用 LPUSH 命令将数据添加到Redis列表
    redis_client.lpush('detections', detection_json)