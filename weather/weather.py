import requests


def get_weather(latitude, longitude):
    """
    Get current weather data using Open-Meteo API.
    """

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "rain,"
            "wind_speed_10m"
        ),
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    current = data["current"]

    return {
        "temperature": current["temperature_2m"],
        "humidity": current["relative_humidity_2m"],
        "rainfall": current["rain"],
        "wind_speed": current["wind_speed_10m"]
    }


def generate_risk_alerts(weather):
    """
    Analyze weather and generate farming risk alerts.
    """

    alerts = []
    recommendations = []

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]
    wind_speed = weather["wind_speed"]

    # HEAT-WAVE RISK
    if temperature >= 40:
        alerts.append("Heat-wave risk detected")
        recommendations.append(
            "Increase irrigation and protect crops from extreme heat."
        )

    # HIGH TEMPERATURE
    elif temperature >= 35:
        alerts.append("High temperature detected")
        recommendations.append(
            "Monitor crops for heat stress and maintain proper irrigation."
        )

    # HEAVY RAIN / FLOOD RISK
    if rainfall >= 20:
        alerts.append("Heavy rainfall or flood risk detected")
        recommendations.append(
            "Check field drainage and avoid additional irrigation."
        )

    # MODERATE RAIN
    elif rainfall >= 5:
        alerts.append("Rainfall detected")
        recommendations.append(
            "Reduce irrigation and monitor water accumulation."
        )

    # DROUGHT / LOW RAINFALL RISK
    elif rainfall == 0:
        alerts.append("Low rainfall detected")
        recommendations.append(
            "Check soil moisture and plan irrigation if required."
        )

    # HIGH HUMIDITY
    if humidity >= 80:
        alerts.append("High humidity detected")
        recommendations.append(
            "Monitor crops for fungal diseases and improve air circulation."
        )

    # LOW HUMIDITY
    elif humidity <= 30:
        alerts.append("Low humidity detected")
        recommendations.append(
            "Monitor crops for moisture stress."
        )

    # HIGH WIND
    if wind_speed >= 40:
        alerts.append("Strong wind risk detected")
        recommendations.append(
            "Protect young plants and avoid spraying pesticides."
        )

    # NORMAL CONDITIONS
    if not alerts:
        alerts.append("No major weather risk detected")
        recommendations.append(
            "Continue regular crop monitoring and irrigation."
        )

    return alerts, recommendations


def weather_report(latitude, longitude):
    """
    Complete weather and agricultural risk report.
    """

    weather = get_weather(latitude, longitude)

    alerts, recommendations = generate_risk_alerts(weather)

    return {
        "weather": weather,
        "alerts": alerts,
        "recommendations": recommendations
    }


if __name__ == "__main__":

    latitude = float(input("Enter latitude: "))
    longitude = float(input("Enter longitude: "))

    try:

        result = weather_report(latitude, longitude)

        print("\nWEATHER DATA")
        print("-------------------")

        print(
            "Temperature:",
            result["weather"]["temperature"],
            "°C"
        )

        print(
            "Humidity:",
            result["weather"]["humidity"],
            "%"
        )

        print(
            "Rainfall:",
            result["weather"]["rainfall"],
            "mm"
        )

        print(
            "Wind Speed:",
            result["weather"]["wind_speed"],
            "km/h"
        )

        print("\nRISK ALERTS")
        print("-------------------")

        for alert in result["alerts"]:
            print("-", alert)

        print("\nRECOMMENDATIONS")
        print("-------------------")

        for recommendation in result["recommendations"]:
            print("-", recommendation)

    except Exception as error:
        print("Error:", error)
