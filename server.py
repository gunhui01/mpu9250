from socket import *
from connection import *

if __name__ == '__main__':
    port = 8080
    i2c1_lo = Mpu(1, "lo")

    server_sock = socket(AF_INET, SOCK_STREAM)
    server_sock.bind(('', port))
    server_sock.listen(1)
    print("%d번 포트로 접속 대기 중..." % port)

    connection_sock, addr = server_sock.accept()
    print(str(addr) + "에서 접속했습니다.")

    rate = 0.1
    compare_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    while True:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        rpy_get = rpy_return(rate, i2c1_lo.calibrationed_agm_data_return())

        if timestamp[-2:] == '00' and timestamp != compare_timestamp:
            compare_timestamp = timestamp
            send_data = timestamp + ',' + str(rpy_get[0]) + ',' + str(rpy_get[1]) + ',' + str(rpy_get[2]) + '\n'
            connection_sock.send(send_data.encode("utf-8"))
            print(timestamp)

        time.sleep(rate)