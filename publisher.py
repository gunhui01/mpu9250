import time
import paho.mqtt.client as mqtt
from data.mpu9250 import Mpu, sensors, str_mpu_addr

BROKER_IP = "192.168.0.100"

def on_connect(client, userdata, flags, rc):
    print("Connected with result code %d", rc)

def on_publish(client, userdata, mid):
    print("Message Published...")

def on_disconnect(client, userdata, rc):
    print(f"Disconnected with result code {rc}")
    if rc != 0:
        print("Unexpected disconnection. Attempting to reconnect...")
        try:
            client.reconnect()
        except Exception as e:
            print(f"Error during reconnection: {e}")

def publish_data():
    while True:
        for sensor in sensors:
            payload = sensor.sensor_id + ',' + sensor.agm_data_return_str()
            print(payload)
            mqttc.publish("imu/data", payload, qos=1)
        time.sleep(1)

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_publish = on_publish
    
mqttc.connect(BROKER_IP, 1883, 60)
mqttc.loop_start()

try:
    publish_data()
except KeyboardInterrupt:
    print("Exiting")
    mqttc.disconnect()
    mqttc.loop_stop()