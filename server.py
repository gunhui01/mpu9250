import json, time
from datetime import *
from socket import *
from data.mpu9250 import Mpu
from data.weather import agm_weather_data_return_str

# 시간 초기화 함수
def data_time():
    now = datetime.now()
    next_second = now.second + 1
    next_minute = now.minute
    next_hour = now.hour
    next_day = now.day

    if next_second >= 60:
        next_second = 0
        next_minute += 1
    if next_minute >= 60:
        next_minute = 0
        next_hour += 1
    if next_hour >= 24:
        next_hour = 0
        next_day += 1

    return now.replace(day=next_day, hour=next_hour, minute=next_minute, second=next_second, microsecond=0)


### API 키, 기상대 ID, 지연시간 불러오기 ###
with open("./config/config.json") as f:
    config = json.load(f)
api_key = config["api_key"]
station_id = config["station_id"]

if __name__ == '__main__':
    port = 8080
    i2c1_lo = Mpu(1, "lo")
    i2c1_hi = Mpu(1, "hi")
    i2c2_lo = Mpu(2, "lo")
    sensors = [i2c1_lo, i2c1_hi, i2c2_lo]

    server_sock = socket(AF_INET, SOCK_STREAM) # 소켓 생성 (IPv4, TCP)
    server_sock.bind(('', port)) # IP와 PORT 지정
    server_sock.listen(1) # 클라이언트 연결 요청까지 기다림
    print("Waiting for connection on %d port..." % port)

    connection_sock, addr = server_sock.accept() # 연결된 클라이언트의 소켓과 주소를 반환함
    print("Connect from " + str(addr))

    # 센서 데이터 전송 함수
    def send_sensor_data(now_str, weather_data):
        for sensor_id in sensors: # sensors 내의 객체 각각 한 번씩 실행
            send_data = f"{sensor_id},{now_str},{sensor_id.agm_data_return_str()}"
            if weather_data != 'no_weather':
                send_data += f",{weather_data}\n"
            else:
                send_data += f"\n"
            connection_sock.send(send_data.encode()) # 생성한 데이터를 UTF-8으로 인코딩하여 전송
            time.sleep(0.1)

    next_data_time = data_time()
    try:

        while True:
            now = datetime.now() # 현재 시간을 저장
            now_str = now.strftime('%Y-%m-%d %H:%M:%S') # 현재 시간을 문자열로 변환
            if now >= next_data_time:
                if now.second == 0:
                    weather_data = agm_weather_data_return_str(api_key, station_id)
                    send_sensor_data(now_str, weather_data)
                    next_data_time = data_time()
                    print(now_str)
                else:
                    send_sensor_data(now_str,'no_weather')
                    next_data_time = data_time()
                    print(now_str)


    except KeyboardInterrupt: # 키보드 인터럽트가 발생한 경우 코드 실행
        print("Server stopped")
        connection_sock.close() # 클라이언트 소켓 닫음
        server_sock.close()
