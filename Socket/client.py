import os
import os.path
from socket import *

def file_check(sensor_id): # 파일의 존재 유무 확인
    dir_name = os.path.dirname(os.path.realpath(__file__)) # 파일 경로 추출
    file_path = f"{dir_name}/{sensor_id}_rpy.csv"

    if not os.path.isfile(file_path): # 파일이 없으면
        with open(file_path, 'w') as file: # 새 파일 생성
            # 데이터 파일에 헤더 추가
            file.write("timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,temperature,humidity,wind_direction,wind_speed,pressure\n")

    return open(file_path, 'a')  # 파일을 쓰기 모드로 반환

if __name__ == '__main__':
    #ip = input("서버의 IP를 입력하세요 : ")
    #port = int(input("서버의 포트를 입력하세요 : "))

    client_sock = socket(AF_INET, SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 8080))
    #print("%d:%d에 접속했습니다.\n", ip, port)

    try:
        while True:
            recv_data = client_sock.recv(1024).decode("utf-8")
            sensor_id, data = recv_data.split(',', 1) # 데이터에서 센서ID 분리
            with file_check(sensor_id) as csv: # 센서ID에 맞는 파일 생성
                csv.write(data)

    except KeyboardInterrupt:
        print("Client stopped")