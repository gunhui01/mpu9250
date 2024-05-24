import asyncio, os
import socket
from datetime import datetime
from config.config_loader import SERVER_IP, SERVER_PORT

# output 파일 관리 클래스
class FileManager:
    def __init__(self):
        self.output_dir = "./output"
        # output 디렉토리가 없으면 생성
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.files = {} # 파일 핸들을 저장할 딕셔너리

    def write_data(self, sensor_id, data):
        file_path = f"{self.output_dir}/{sensor_id}.csv"

        # 파일 핸들이 열려있지 않다면 아래 코드 실행
        if sensor_id not in self.files:
            # 파일이 없으면 새로 생성하고, 파일이 비어있는 경우 헤더 추가
            if not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write("timestamp,ACCEL_X,ACCEL_Y,ACCEL_Z,GYRO_X,GYRO_Y,GYRO_Z,MAG_X,MAG_Y,MAG_Z,roll,pitch,yaw,temperature,humidity,wind_direction,wind_speed,pressure\n")
            # 파일이 있으면 파일 열기
            self.files[sensor_id] = open(file_path, 'a')
        self.files[sensor_id].write(data + '\n')
    
    # 해당 센서의 파일이 열려있다면 닫고 딕셔너리에서 제거
    def close_file(self, sensor_id):
        if sensor_id in self.files:
            self.files[sensor_id].close()
            del self.files[sensor_id]

    # 모든 열린 파일 닫고 딕셔너리 비우기
    def close_all_files(self):
        for sensor_id in list(self.files):
            self.close_file(sensor_id)
fm = FileManager()


async def main():
    client_sock = None # 예외 처리용 소켓 초기화
    try:
        while True:
            try:
                client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_sock.connect((SERVER_IP, SERVER_PORT))
                client_sock.settimeout(5)
                print(f"Connected to {SERVER_IP}.")
                print("Receiving data from the server...")

                buffer = ""

                try:
                    while True:
                        recv_data = client_sock.recv(1024).decode()
                        if not recv_data:
                            print("Server disconnected")
                            break
                        ### 데이터가 연속적으로 전송되는 경우를 대비하여 버퍼에 데이터 추가 ###
                        buffer += recv_data
                        while '\n' in buffer:
                            recv_data, buffer = buffer.split('\n', 1) # 데이터를 개행문자를 기준으로 분리
                            sensor_id, data = recv_data.split(',', 1) # 데이터에서 센서ID 분리
                            fm.write_data(sensor_id, data)

                finally:
                    if client_sock:
                        client_sock.close()

            except socket.error as e:
                    error_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{error_time} Connection failed: {e}")

            print(f"Try reconnecting in 5 seconds...")
            await asyncio.sleep(5)

    finally:
        fm.close_all_files()
        if client_sock:
            client_sock.close()
        print("Socket connection closed")


if __name__ == "__main__":
    try:asyncio.run(main())
    except KeyboardInterrupt:
        print("Client stopped by user input(Ctrl + C)")
    except asyncio.CancelledError:
        print("Client stopped by user input(Ctrl + C)")