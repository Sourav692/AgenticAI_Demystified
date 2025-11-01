import os
import requests
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

OPENWEATHERMAP_API_KEY = ""

# Initialize the FastMCP server
mcp = FastMCP("WeatherAssistant")

@mcp.resource("file://delivery_log")
def delivery_log_resource() -> list[str]:
    """
    Reads a delivery log file and returns its contents as a list of lines.
    Each line contains an order number and a delivery location.
    """
    try:
        log_file = Path("delivery_log.txt")
        if not log_file.exists():
            return ["Error: The delivery_log.txt file was not found on the server."]
        
        # Read the file, remove leading/trailing whitespace, and split into lines
        return log_file.read_text(encoding="utf-8").strip().splitlines()
        
    except Exception as e:
        return [f"An unexpected error occurred while reading the delivery log: {str(e)}"]

@mcp.tool()
def get_weather(location: str) -> dict:
    """
    Fetches the current weather for a specified location using the OpenWeatherMap API.

    Args:
        location: The city name and optional country code (e.g., "London,uk").

    Returns:
        A dictionary containing weather information or an error message.
    """
    if not OPENWEATHERMAP_API_KEY or OPENWEATHERMAP_API_KEY == "YOUR_OPENWEATHERMAP_API_KEY":
        return {"error": "OpenWeatherMap API key is not configured on the server."}

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": OPENWEATHERMAP_API_KEY,
        "units": "metric"  # Use "imperial" for Fahrenheit
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx or 5xx)

        data = response.json()

        # Extracting relevant weather information
        weather_description = data["weather"][0]["description"]
        temperature = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return {
            "location": data["name"],
            "weather": weather_description,
            "temperature_celsius": f"{temperature}°C",
            "feels_like_celsius": f"{feels_like}°C",
            "humidity": f"{humidity}%",
            "wind_speed_mps": f"{wind_speed} m/s"
        }

    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            return {"error": f"Could not find weather data for '{location}'. Please check the location name."}
        elif response.status_code == 401:
            return {"error": "Authentication failed. The API key is likely invalid or inactive."}
        else:
            return {"error": f"An HTTP error occurred: {http_err}"}
    except requests.exceptions.RequestException as req_err:
        return {"error": f"A network error occurred: {req_err}"}
    except KeyError:
        return {"error": "Received unexpected data format from the weather API."}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}


if __name__ == "__main__":
    logging.getLogger("mcp").setLevel(logging.WARNING)
    # The server will run and listen for requests from the client over stdio
    mcp.run(transport="stdio")