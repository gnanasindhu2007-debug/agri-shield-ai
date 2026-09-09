import requests


# -----------------------------
# WEATHER API
# -----------------------------
def get_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation_probability",
            "precipitation",
            "wind_speed_10m",
            "soil_moisture_0_to_1cm"
        ],
        "forecast_days": 3,
        "timezone": "auto"
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("Weather API Error")
        return None

    return response.json()


# -----------------------------
# WEATHER ANALYSIS
# -----------------------------
def analyze_weather(weather):

    hourly = weather["hourly"]

    temperature = hourly["temperature_2m"][0]
    humidity = hourly["relative_humidity_2m"][0]
    rain_probability = hourly["precipitation_probability"][0]
    rainfall = hourly["precipitation"][0]
    wind_speed = hourly["wind_speed_10m"][0]
    soil_moisture = hourly["soil_moisture_0_to_1cm"][0]

    return {
        "temperature": temperature,
        "humidity": humidity,
        "rain_probability": rain_probability,
        "rainfall": rainfall,
        "wind_speed": wind_speed,
        "soil_moisture": soil_moisture
    }


# -----------------------------
# CROP RECOMMENDATION ENGINE
# -----------------------------
def generate_recommendation(data, crop):

    temperature = data["temperature"]
    humidity = data["humidity"]
    rain_probability = data["rain_probability"]
    rainfall = data["rainfall"]
    wind_speed = data["wind_speed"]
    soil_moisture = data["soil_moisture"]

    recommendations = []

    # Irrigation recommendation
    if rain_probability >= 60 or rainfall >= 5:
        recommendations.append(
            "Avoid irrigation now because rainfall is expected."
        )

    elif soil_moisture >= 0.30:
        recommendations.append(
            "Irrigation may not be required because soil moisture is sufficient."
        )

    else:
        recommendations.append(
            "Consider irrigation if the crop requires water."
        )

    # Fertilizer recommendation
    if rain_probability >= 60 or rainfall >= 5:
        recommendations.append(
            "Postpone fertilizer application because rain is expected."
        )
    else:
        recommendations.append(
            "Weather is relatively suitable for fertilizer application."
        )

    # Spraying recommendation
    if wind_speed >= 20:
        recommendations.append(
            "Avoid pesticide spraying because wind speed is high."
        )
    elif rain_probability >= 60:
        recommendations.append(
            "Avoid spraying because rain is likely."
        )
    else:
        recommendations.append(
            "Weather conditions are relatively suitable for spraying."
        )

    # Heat warning
    if temperature >= 35:
        recommendations.append(
            "Heat stress warning: monitor the crop and maintain adequate moisture."
        )

    # Disease weather risk
    if humidity >= 80 and rain_probability >= 60:
        recommendations.append(
            "High humidity and rainfall may favor disease development. "
            "Monitor the crop closely."
        )

    return recommendations


# -----------------------------
# MAIN PROGRAM
# -----------------------------
if __name__ == "__main__":

    print("====================================")
    print(" AI WEATHER CROP RECOMMENDATION")
    print("====================================")

    # Example location: Guntur
    latitude = 16.3067
    longitude = 80.4365

    crop = input("Enter crop name: ")

    print("\nFetching weather data...")

    weather = get_weather(latitude, longitude)

    if weather is None:
        exit()

    data = analyze_weather(weather)

    print("\n------ CURRENT WEATHER ------")

    print("Temperature :", data["temperature"], "°C")
    print("Humidity    :", data["humidity"], "%")
    print("Rain Chance :", data["rain_probability"], "%")
    print("Rainfall    :", data["rainfall"], "mm")
    print("Wind Speed  :", data["wind_speed"], "km/h")
    print("Soil Moist. :", data["soil_moisture"])

    print("\n------ RECOMMENDATIONS ------")

    recommendations = generate_recommendation(data, crop)

    for i, recommendation in enumerate(recommendations, 1):
        print(f"{i}. {recommendation}")
