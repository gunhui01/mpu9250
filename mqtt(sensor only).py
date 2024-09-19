import time, requests, warnings, socket
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
warnings.filterwarnings("ignore", category=DeprecationWarning)
from config.config_loader import INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET


client_id = f"mqtt_{socket.gethostname()}" # hostname을 client_id로 설정

# InfluxDB client 설정
client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("imu/data", qos=1) #QoS 1로 설정(최소한 한 번 전달)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    imu_data = payload.split(',')
    print(imu_data)
    # point = influxdb_client.Point("imu")\
    #         .tag("id", imu_data[0])\
    #         .field("acc_x", float(imu_data[1]))\
    #         .field("acc_y", float(imu_data[2]))\
    #         .field("acc_z", float(imu_data[3]))\
    #         .field("gyro_x", float(imu_data[4]))\
    #         .field("gyro_y", float(imu_data[5]))\
    #         .field("gyro_z", float(imu_data[6]))\
    #         .field("mag_x", float(imu_data[7]))\
    #         .field("mag_y", float(imu_data[8]))\
    #         .field("mag_z", float(imu_data[9]))
    # write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id, clean_session=False)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("192.168.0.200", 1883, 60)
mqttc.loop_start()


# 무한 루프로 클라이언트 유지
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting")
    mqttc.disconnect()
    mqttc.loop_stop()