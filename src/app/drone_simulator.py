import time  
import random  
import math  
from dataclasses import dataclass  

@dataclass  
class DroneState:  
    timestamp: float  
    latitude: float    # 纬度  
    longitude: float   # 经度  
    altitude: float    # 高度  
    speed: float       # 速度  
    pitch: float       # 俯仰角  
    roll: float        # 横滚角  
    battery: float     # 电量  
    signal_strength: int  

class DroneSimulator:  
    def __init__(self, base_lat=29.5806, base_lon=106.5523):  # 重庆坐标  
        self.state = DroneState(  
            timestamp=time.time(),  
            latitude=base_lat,  
            longitude=base_lon,  
            altitude=100.0,  
            speed=10.0,  
            pitch=0.0,  
            roll=0.0,  
            battery=100.0,  
            signal_strength=5  
        )  
        self._running = False  

    def _update_state(self):  
        t = time.time()  
        # 模拟圆周运动 (半径500米)  
        self.state.longitude += math.sin(t * 0.1) * 0.0045  # ~500米变化  
        self.state.latitude += math.cos(t * 0.1) * 0.0045  
        self.state.altitude = 100 + 50 * math.sin(t * 0.5)  
        self.state.speed = 10 + 5 * math.sin(t)  
        self.state.battery = max(0, self.state.battery - 0.01)  
        self.state.pitch = 5 * math.sin(t * 2)  
        self.state.roll = 5 * math.cos(t * 2)  

    def start(self, callback):  
        self._running = True  
        while self._running:  
            self._update_state()  
            callback(self.state)  
            time.sleep(0.1)  # 100ms更新一次  

    def stop(self):  
        self._running = False  