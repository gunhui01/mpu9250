import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 상위 디렉토리의 파일을 import하기 위한 설정
from socket import *
from Sensor.mpu9250 import *
from Sensor.weather import *


api_key = "API_KEY"
station_id = "STATION_ID"

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

    rate = 1
    compare_timestamp = time.strftime("%Y-%m-%d %H:%M:%S") # 현재 시간을 저장

    try:
        while True:
            for sensor_id in sensors: # sensors 객체들 각각 한 번씩 실행
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S") # 현재 시간을 저장
                rpy_get_sensor = rpy_return(rate, sensor_id.calibrationed_agm_data_return()) # 센서 데이터 받아옴

                if timestamp[-2:] == '00' and timestamp != compare_timestamp: # 현재 시간이 00초이고, 이전 데이터를 보낸 시간과 현재 시간이 다른 경우 코드 실행
                    
                    rpy_get_weather = rpy_return(rate, agm_weather_data_return()) # 기상 데이터 받아옴
                    send_data = f"{sensor_id},{timestamp},{rpy_get_sensor},{rpy_get_weather}\n" # 보낼 데이터 문자열에 현재 시간과 데이터 값 추가
                    connection_sock.send(send_data.encode("utf-8")) # 생성한 데이터를 클라이언트에게 UTF-8으로 인코딩하여 전송
                    print(timestamp) # 현재 시간을 출력
                    

                else: # 위 조건이 아닌 경우 코드 실행
                    send_data = f"{sensor_id},{timestamp},{rpy_get_sensor}\n" # 보낼 데이터 문자열에 현재 시간과 데이터 값 추가
                    connection_sock.send(send_data.encode("utf-8")) # 생성한 데이터를 클라이언트에게 UTF-8으로 인코딩하여 전송

                compare_timestamp = timestamp # 이전 시간을 현재 시간으로 업데이트
                time.sleep(rate) # 센서 데이터 전송 후 rate만큼 지연 (데이터가 빠르게 전송되는 것을 방지)
    
    except KeyboardInterrupt: # 키보드 인터럽트가 발생한 경우 코드 실행
        print("Server stopped")
        connection_sock.close() # 클라이언트 소켓 닫음
        server_sock.close()