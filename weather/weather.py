import requests


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def get_weather(latitude, longitude):
    """
    Get current weather data from the Open-Meteo API.
    """

    # Validate coordinates
    if not -90 <= latitude <= 90:
        raise ValueError("Latitude must be between -90 and 90.")

    if not -180 <= longitude <= 180:
        raise ValueError("Longitude must be between -180 and 180.")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "rain,"
            "wind_speed_10m"
        ),
        "timezone": "auto",
    }

    try:
        response = requests.get(
            OPEN_METEO_URL,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        data = response.json()

        current = data.get("current")

        if not current:
            raise ValueError("Weather data is unavailable.")

        return {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "rainfall": current.get("rain"),
            "wind_speed": current.get("wind_speed_10m"),
        }

    except requests.exceptions.Timeout:
        raise ConnectionError(
            "Weather service timed out. Please try again."
        )

    except requests.exceptions.RequestException as error:
        raise ConnectionError(
            f"Unable to fetch weather data: {error}"
        )


def generate_risk_alerts(weather):
    """
    Analyze current weather conditions and generate
    farmer-friendly agricultural risk alerts.
    """

    alerts = []
    recommendations = []

    temperature = weather["temperature"]
    humidity = weather["humidity"]
    rainfall = weather["rainfall"]
    wind_speed = weather["wind_speed"]

    # ------------------------------------------------
    # HEAT-WAVE RISK
    # ------------------------------------------------
    if temperature >= 40:

        alerts.append("Extreme heat risk detected")

        recommendations.append(
            "Increase irrigation when needed and protect crops "
            "from extreme heat."
        )

    # ------------------------------------------------
    # HIGH TEMPERATURE
    # ------------------------------------------------
    elif temperature >= 35:

        alerts.append("High temperature detected")

        recommendations.append(
            "Monitor crops for heat stress and maintain "
            "adequate soil moisture."
        )

    # ------------------------------------------------
    # HEAVY RAINFALL
    # ------------------------------------------------
    if rainfall >= 20:

        alerts.append("Heavy rainfall detected")

        recommendations.append(
            "Check field drainage and avoid unnecessary irrigation."
        )

    # ------------------------------------------------
    # MODERATE RAINFALL
    # ------------------------------------------------
    elif rainfall >= 5:

        alerts.append("Rainfall detected")

        recommendations.append(
            "Reduce irrigation and check for water accumulation "
            "in the field."
        )

    # ------------------------------------------------
    # NO CURRENT RAIN
    # ------------------------------------------------
    elif rainfall == 0:

        alerts.append("No current rainfall detected")

        recommendations.append(
            "Check soil moisture and irrigate if the crop requires water."
        )

    # ------------------------------------------------
    # HIGH HUMIDITY
    # ------------------------------------------------
    if humidity >= 80:

        alerts.append("High humidity detected")

        recommendations.append(
            "Monitor crops for fungal diseases and improve "
            "air circulation."
        )

    # ------------------------------------------------
    # LOW HUMIDITY
    # ------------------------------------------------
    elif humidity <= 30:

        alerts.append("Low humidity detected")

        recommendations.append(
            "Monitor crops for moisture stress and maintain "
            "proper soil moisture."
        )

    # ------------------------------------------------
    # STRONG WIND
    # ------------------------------------------------
    if wind_speed >= 40:

        alerts.append("Strong wind risk detected")

        recommendations.append(
            "Protect young plants and avoid spraying pesticides "
            "during strong winds."
        )

    # ------------------------------------------------
    # NORMAL CONDITIONS
    # ------------------------------------------------
    if not alerts:

        alerts.append("Weather conditions are normal")

        recommendations.append(
            "Continue regular crop monitoring and irrigation "
            "according to soil moisture."
        )

    return alerts, recommendations


def weather_report(latitude, longitude):
    """
    Generate a complete weather and agricultural
    risk report.
    """

    weather = get_weather(latitude, longitude)

    alerts, recommendations = generate_risk_alerts(weather)

    return {
        "weather": weather,
        "alerts": alerts,
        "recommendations": recommendations,
    }


# ----------------------------------------------------
# MAIN PROGRAM
# ----------------------------------------------------

if __name__ == "__main__":

    print("\n🌱 AGRI-SHIELD AI - WEATHER MONITOR")
    print("-----------------------------------")

    try:

        latitude = float(
            input("Enter latitude: ")
        )

        longitude = float(
            input("Enter longitude: ")
        )

        result = weather_report(
            latitude,
            longitude
        )

        weather = result["weather"]

        print("\n🌦️ CURRENT WEATHER")
        print("-------------------------")

        print(
            f"Temperature : {weather['temperature']} °C"
        )

        print(
            f"Humidity    : {weather['humidity']} %"
        )

        print(
            f"Rainfall    : {weather['rainfall']} mm"
        )

        print(
            f"Wind Speed  : {weather['wind_speed']} km/h"
        )

        print("\n⚠️ FARMING RISK ALERTS")
        print("-------------------------")

        for alert in result["alerts"]:

            print(f"• {alert}")

        print("\n🌾 FARMER RECOMMENDATIONS")
        print("-------------------------")

        for recommendation in result["recommendations"]:

            print(f"• {recommendation}")

        print("\n✅ Weather analysis completed.")

    except ValueError as error:

        print(f"\n❌ Input Error: {error}")

    except ConnectionError as error:

        print(f"\n❌ Weather Error: {error}")

    except Exception as error:

        print(f"\n❌ Unexpected Error: {error}")
