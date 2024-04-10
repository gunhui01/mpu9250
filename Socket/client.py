import os
import os.path
from socket import *

def file_check():
    dir_name = os.path.dirname(os.path.realpath(__file__))

    if not os.path.isfile(dir_name + "/rpy.csv"):
        os.system("touch " + dir_name + "/rpy.csv")
        os.system("echo timestamp,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,mag_x,mag_y,mag_z,temperature,humidity,wind_direction,wind_speed,pressure >> " + dir_name + "/rpy.csv")

    return open(dir_name + "/rpy.csv", 'a')

if __name__ == '__main__':
    #ip = input("서버의 IP를 입력하세요 : ")
    #port = int(input("서버의 포트를 입력하세요 : "))

    csv = file_check()

    client_sock = socket(AF_INET, SOCK_STREAM)
    client_sock.connect(('127.0.0.1', 8080))
    #print("%d:%d에 접속했습니다.\n", ip, port)

    try:
        while True:
            recv_data = client_sock.recv(1024)
            csv.write(recv_data.decode("utf-8"))
    except KeyboardInterrupt:
        csv.close()