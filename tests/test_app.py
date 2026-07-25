from app import app, db, WeatherLog, Favorite, get_activity_recommendation, health_check
from unittest.mock import patch

# Testing the valid zip code fetches mock API data and successfully saves the location to the database.
@patch('app.requests.get')
def test_weather_search(mock_get, client):
    fake_json_data = {"location": {
        "name": "Jersey City"
    },
    "current": {
        "temp_f": 72.0, "condition": {"text": "Sunny"}
    },
    "forecast": {
        "forecastday" : [{"day" : {"maxtemp_f": 72.0, "mintemp_f": 67.0, "avgtemp_f" : 70.0}}]
    }}
    mock_get.return_value.json.return_value = fake_json_data
    response = client.post('/get_weather', data={'zipcode': '07302'})
    assert response.status_code == 200
    with app.app_context():
        log_entry = WeatherLog.query.first()
        assert log_entry is not None
        assert log_entry.location_name == "Jersey City"

# Testing if there is a bad zip code inserted.
@patch('app.requests.get')
def test_bad_zipcode(mock_get, client):
    fake_error_json = {
        "error": {
            "message": "No matching location found."
        }
    }
    mock_get.return_value.json.return_value = fake_error_json
    response = client.post('/get_weather', data={'zipcode': '00000'})
    assert response.status_code == 200
    assert b"Try again" in response.data

#Testing if the activity logic works
def test_activity_logic1():
    options = get_activity_recommendation(80.0, "Cloudy")
    assert "Comfortable enough for a walk." in options
    assert "Call your friends to meet!" in options

def test_activity_logic2():
    options = get_activity_recommendation(65.0, "Sunny")
    assert "A fantastic day to travel around." in options
    assert "Don't forget your groceries" in options

def test_health_check(client):
    response = client.get('/health_check')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}