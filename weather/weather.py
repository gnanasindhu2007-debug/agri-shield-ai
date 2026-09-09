import requests


def get_weather(latitude, longitude):
    """
    Get current weather data using Open-Meteo API.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,relative_humidity_2m,rain,weather_code,wind_speed_10m",
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    current = data["current"]

    weather = {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "rainfall": current["rain"],
        "weather_code": current["weather_code"],
        "wind_speed": current["wind_speed_10m"]
    }

    return weather


def generate_risk_alert(weather):
    """
    Generate simple agricultural risk alerts
    based on weather conditions.
    """

    alerts = []
    recommendations = []

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]

    # Heat risk
    if temperature >= 38:
        alerts.append("High heat risk")
        recommendations.append(
            "Increase irrigation and monitor crops for heat stress."
        )

    # Heavy rainfall
    if rainfall >= 20:
        alerts.append("Heavy rainfall risk")
        recommendations.append(
            "Check field drainage and avoid unnecessary irrigation."
        )

    # Low rainfall
    if rainfall < 1:
        alerts.append("Low recent rainfall")
        recommendations.append(
            "Check soil moisture before irrigation."
        )

    # High humidity
    if humidity >= 80:
        alerts.append("High humidity")
        recommendations.append(
            "Monitor crops for possible fungal disease development."
        )

    if not alerts:
        alerts.append("No major weather risk detected")

    return alerts, recommendations


def weather_report(latitude, longitude):
    """
    Get weather data and generate agricultural alerts.
    """

    weather = get_weather(latitude, longitude)

    alerts, recommendations = generate_risk_alert(weather)

    return {
        "weather": weather,
        "alerts": alerts,
        "recommendations": recommendations
    }


if __name__ == "__main__":

    print("🌦️ AGRI-SHIELD AI Weather Module")

    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    try:
        result = weather_report(latitude, longitude)

        weather = result["weather"]

        print("\n🌦️ CURRENT WEATHER")
        print("-------------------------")
        print("Temperature:", weather["temperature"], "°C")
        print("Humidity:", weather["humidity"], "%")
        print("Rainfall:", weather["rainfall"], "mm")
        print("Wind Speed:", weather["wind_speed"], "km/h")

        print("\n⚠️ RISK ALERTS")
        print("-------------------------")
        for alert in result["alerts"]:
            print("-", alert)

        print("\n💡 RECOMMENDATIONS")
        print("-------------------------")
        for recommendation in result["recommendations"]:
            print("-", recommendation)

    except Exception as error:
        print("\n❌ Error:", error)
