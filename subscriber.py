import time, warnings, socket
import paho.mqtt.client as mqtt
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
from data.weather import return_weather_data
from config.config_loader import API_KEY, STATION_ID, INFLUXDB_BUCKET, INFLUXDB_ORG, INFLUXDB_TOKEN, INFLUXDB_URL
#warnings.filterwarnings("ignore", category=DeprecationWarning)

client_id = f"mqtt_{socket.gethostname()}" # hostname을 client_id로 설정

# InfluxDB client 설정
client = influxdb_client.InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

start = int(time.time())

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("imu/data", qos=1) #QoS 1로 설정(최소한 한 번 전달)

def on_message(client, userdata, msg):
    global start
    payload = msg.payload.decode()
    imu_data = payload.split(',')
    print(imu_data)

    def safe_float_conversion(value):
        try:
            return float(value)
        except ValueError:
            return None
        
    def safe_int_conversion(value):
        try:
            return int(value)
        except ValueError:
            return None

    point = influxdb_client.Point("imu")\
            .tag("id", imu_data[0])\
            .field("acc_x", safe_float_conversion(imu_data[1]))\
            .field("acc_y", safe_float_conversion(imu_data[2]))\
            .field("acc_z", safe_float_conversion(imu_data[3]))\
            .field("gyro_x", safe_float_conversion(imu_data[4]))\
            .field("gyro_y", safe_float_conversion(imu_data[5]))\
            .field("gyro_z", safe_float_conversion(imu_data[6]))\
            .field("mag_x", safe_float_conversion(imu_data[7]))\
            .field("mag_y", safe_float_conversion(imu_data[8]))\
            .field("mag_z", safe_float_conversion(imu_data[9]))\
            .time(safe_int_conversion(imu_data[10]))
    write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

    # if not (int(time.time()) - start) % 60:
    #     start = int(time.time())
    #     weather_data = return_weather_data(API_KEY, STATION_ID)
    #     if not weather_data == "N/A":
    #         point = influxdb_client.Point("weather")\
    #                 .field("temperature", weather_data[0])\
    #                 .field("humidity", weather_data[1])\
    #                 .field("wind_direction", weather_data[2])\
    #                 .field("wind_speed", weather_data[3])\
    #                 .field("pressure", weather_data[4])\
    #                 .time(int(time.time() * 1000000000))
    #         write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

# mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, client_id, clean_session=False)
mqttc = mqtt.Client(client_id, clean_session=False)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", 1883, 60)
mqttc.loop_start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting")
    mqttc.disconnect()
    mqttc.loop_stop()
