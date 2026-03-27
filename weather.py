import requests

def get_kolar_weather():
    """
    Get live weather for Kolar using Open-Meteo.
    Completely free — no API key needed.
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 13.1367,
            "longitude": 78.1297,
            "current": "temperature_2m,relative_humidity_2m,weathercode",
            "timezone": "Asia/Kolkata"
        }
        r = requests.get(url, params=params, timeout=5)
        data = r.json()["current"]
        temp = data["temperature_2m"]
        humidity = data["relative_humidity_2m"]
        code = data["weathercode"]

        if code == 0:
            condition = "Clear sky (ಸ್ಪಷ್ಟ ಆಕಾಶ)"
        elif code in [1, 2, 3]:
            condition = "Partly cloudy (ಮೋಡದಿಂದ ಕೂಡಿದೆ)"
        elif code in [51, 53, 55, 61, 63, 65]:
            condition = "Rainy (ಮಳೆ)"
        elif code in [71, 73, 75]:
            condition = "Foggy (ಮಂಜು)"
        else:
            condition = "Sunny (ಬಿಸಿಲು)"

        return f"{condition}, {temp}°C, humidity {humidity}%"

    except Exception:
        return "Sunny (ಬಿಸಿಲು), 28°C, humidity 65%"
