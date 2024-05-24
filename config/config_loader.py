import json

def load_config():
    global API_KEY, STATION_ID, SERVER_IP, SERVER_PORT, MAX_I2C_BUS_COUNT
    with open("./config/config.json") as f:
        config = json.load(f)

    API_KEY = config["API_KEY"]
    STATION_ID = config["STATION_ID"]
    SERVER_IP = config["SERVER_IP"]
    SERVER_PORT = int(config["SERVER_PORT"])
    MAX_I2C_BUS_COUNT = int(config["MAX_I2C_BUS_COUNT"])

load_config()