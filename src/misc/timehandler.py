import time
from ping3 import ping


class TimeHandler:
    def __init__(self):
        self.__startTime = None
    
    def startTimer(self):
        self.__startTime = time.time()
        
    def stopTimer(self):
        return time.time() - self.__startTime
    
    def pingServer(self, endpoint):
        latency = ping(endpoint, unit="ms")
        return round(latency, 2)
