import time, requests, warnings, socket
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
warnings.filterwarnings("ignore", category=DeprecationWarning)

BUCKET = "sensor"
ORG = "ssspa"
TOKEN = "Y8_2xS1QJCSLcC7wND28PW-WVj7qqIgL4sqQrWNpzt0YrAlytgpFCYWeYe5iAh8GvdWQZKAF7UnNfsGhpxFTdA=="
URL = "http://192.168.0.100:8086"
client_id = f"mqtt_{socket.gethostname()}" # hostname을 client_id로 설정

# InfluxDB client 설정
client = influxdb_client.InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("imu/data", qos=1) #QoS 1로 설정(최소한 한 번 전달)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    imu_data = payload.split(',')
    print(imu_data)
    point = influxdb_client.Point("imu")\
            .tag("id", imu_data[0])\
            .field("acc_x", float(imu_data[1]))\
            .field("acc_y", float(imu_data[2]))\
            .field("acc_z", float(imu_data[3]))\
            .field("gyro_x", float(imu_data[4]))\
            .field("gyro_y", float(imu_data[5]))\
            .field("gyro_z", float(imu_data[6]))\
            .field("mag_x", float(imu_data[7]))\
            .field("mag_y", float(imu_data[8]))\
            .field("mag_z", float(imu_data[9]))
    write_api.write(bucket=BUCKET, org=ORG, record=point)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id, clean_session=False)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()


# 무한 루프로 클라이언트 유지
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting")
    mqttc.disconnect()
    mqttc.loop_stop()