import os
import requests
import logging
from mcp.server.fastmcp import FastMCP

OPENWEATHERMAP_API_KEY = ""

# Initialize the FastMCP server
mcp = FastMCP("WeatherAssistant")

@mcp.prompt()
def compare_weather_prompt(location_a: str, location_b: str) -> str:
    """
    Generates a clear, comparative summary of the weather between two specified locations.
    This is the best choice when a user asks to compare, contrast, or see the difference in weather between two places.
    
    Args:
        location_a: The first city for comparison (e.g., "London").
        location_b: The second city for comparison (e.g., "Paris").
    """
    return f"""
    You are acting as a helpful weather analyst. Your goal is to provide a clear and easy-to-read comparison of the weather in two different locations for a user.

    The user wants to compare the weather between "{location_a}" and "{location_b}".

    To accomplish this, follow these steps:
    1.  First, gather the necessary weather data for both "{location_a}" and "{location_b}".
    2.  Once you have the weather data for both locations, DO NOT simply list the raw results.
    3.  Instead, synthesize the information into a concise summary. Your final response should highlight the key differences, focusing on temperature, the general conditions (e.g., 'sunny' vs 'rainy'), and wind speed.
    4.  Present the comparison in a structured format, like a markdown table or a clear bulleted list, to make it easy for the user to understand at a glance.
    """

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