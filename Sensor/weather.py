import requests
import json

def weather_return(api_key, station_id):
    response = requests.get(f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=s&apiKey={api_key}")
    data = response.json()
    weather_dict = dict()

    weather_dict["time"] = data["observations"][0]["obsTimeLocal"]
    weather_dict["solar_radiation"] = data["observations"][0]["solarRadiation"]
    weather_dict["longitude"] = data["observations"][0]["lon"]
    weather_dict["latitude"] = data["observations"][0]["lat"]
    weather_dict["uv"] = data["observations"][0]["uv"]
    weather_dict["humidity"] = data["observations"][0]["humidity"]
    weather_dict["temperature"] = data["observations"][0]["metric_si"]['temp']
    weather_dict["heat_index"] = data["observations"][0]["metric_si"]['heatIndex']
    weather_dict["dew_point"] = data["observations"][0]["metric_si"]['dewpt']
    weather_dict["wind_direction"] = data["observations"][0]['winddir']
    weather_dict["wind_chill"] = data["observations"][0]["metric_si"]['windChill']
    weather_dict["wind_speed"] = data["observations"][0]["metric_si"]['windSpeed']
    weather_dict["wind_gust"] = data["observations"][0]["metric_si"]['windGust']
    weather_dict["pressure"] = data["observations"][0]["metric_si"]['pressure']
    weather_dict["precipitation_rate"] = data["observations"][0]["metric_si"]['precipRate']
    weather_dict["pricipitation_total"] = data["observations"][0]["metric_si"]['precipTotal']
    weather_dict["elevation"] = data["observations"][0]["metric_si"]['elev']

    return weather_dict

### 특정 기상 데이터 반환 ###
def agm_weather_data_return(self, api_key, station_id):

    weather_data = weather_return(api_key, station_id) #기상대 데이터 받아오기
    
    tmp = weather_data["temperature"]
    hum = weather_data["humidity"]
    wind_dir = weather_data["wind_direction"]
    wind_speed = weather_data["wind_speed"]
    pressure = weather_data["pressure"]

    return tmp, hum, wind_dir, wind_speed, pressure

### 기상 데이터를 문자열로 변환하여 반환하는 함수 ###
def agm_weather_data_return_str(self, api_key, station_id):
    return ','.join(map(str, agm_weather_data_return(api_key, station_id)))