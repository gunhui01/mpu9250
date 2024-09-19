import json

def load_config():
    global API_KEY, STATION_ID, SOCKET_SERVER_IP, SOCKET_SERVER_PORT, MAX_I2C_BUS_COUNT, INFLUXDB_URL, INFLUXDB_TOKEN, INFLUXDB_ORG, INFLUXDB_BUCKET, MQTT_BROKER_IP
    with open("./config/config.json") as f:
        config = json.load(f)

    API_KEY = config["API_KEY"]
    STATION_ID = config["STATION_ID"]
    SOCKET_SERVER_IP = config["SOCKET_SERVER_IP"]
    SOCKET_SERVER_PORT = int(config["SOCKET_SERVER_PORT"])
    MAX_I2C_BUS_COUNT = int(config["MAX_I2C_BUS_COUNT"])
    INFLUXDB_URL = config["INFLUXDB_URL"]
    INFLUXDB_TOKEN = config["INFLUXDB_TOKEN"]
    INFLUXDB_ORG = config["INFLUXDB_ORG"]
    INFLUXDB_BUCKET = config["INFLUXDB_BUCKET"]
    MQTT_BROKER_IP = config["MQTT_BROKER_IP"]

load_config()