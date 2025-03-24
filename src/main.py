import hashlib
import time  
import json  
import os  
import random
from app.http_client import HTTPClient  
from app.drone_simulator import DroneSimulator, DroneState  

def map_to_legacy_format(state: DroneState) -> dict:
    """生成完全匹配 SQL 表结构的数据"""
    # 生成数据字典
    data = {
        'altitude': round(state.altitude, 2),
        'speed': round(state.speed, 2),
        'coordinates': f"{state.longitude:.6f},{state.latitude:.6f}",
        'battery_level': round(state.battery, 2),
        'wind_speed': round(random.uniform(0.0, 15.0), 2),
        'position': json.dumps([
            round(state.pitch, 2),
            round(state.roll, 2),
            round(state.altitude, 2)
        ])
    }

    # 将数据字典转换为 JSON 字符串，保证键的顺序一致
    data_str = json.dumps(data, sort_keys=True)

    # 使用 SHA-256 哈希算法对 JSON 字符串进行加密
    hash_object = hashlib.sha256(data_str.encode())
    hashed_data = hash_object.hexdigest()  # 获取哈希值

    # 返回加密后的哈希值
    return {'hashed_data': hashed_data} 

def main():  
    client = HTTPClient()  
    simulator = DroneSimulator()  

    # 从环境变量获取凭证  
    username = os.getenv('DRONE_USERNAME', 'user0002')  
    password = os.getenv('DRONE_PASSWORD', 'user123')  # 默认密码策略  
    
    # 启动模拟器线程  
    import threading  
    sim_thread = threading.Thread(target=simulator.start, args=(lambda x: None,))  
    sim_thread.daemon = True  
    sim_thread.start()  

    if client.login(username, password):  # 使用动态凭证  
        print(f"[{username}] 登录成功，开始发送数据...")  
        try:  
            while True:  
                data = map_to_legacy_format(simulator.state)  
                print(f"[{username}] 发送数据:", data)  
                status, resp = client.invoke_drone_api('drone/send_data', 'POST', data)  
                print(f"[{username}] 状态码: {status}, 响应: {resp[:50]}")  
                time.sleep(10)  
        except KeyboardInterrupt:  
            simulator.stop()  
            print(f"[{username}] 已停止")  
    else:  
        print(f"[{username}] 登录失败")  

if __name__ == '__main__':  
    main()  