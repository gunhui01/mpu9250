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