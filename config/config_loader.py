import json

def load_config():
    global api_key, station_id, server_ip, server_port
    with open("./config/config.json") as f:
        config = json.load(f)

    api_key = config["api_key"]
    station_id = config["station_id"]
    server_ip = config["server_ip"]
    server_port = int(config["server_port"])

load_config()