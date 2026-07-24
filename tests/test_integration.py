from app import app, db, Favorite

# Testing integration of Home page with its HTML file
def test_homepage_integration(client):
    response = client.get('/')  
    assert response.status_code == 200
    assert b"How's The Weather" in response.data


# Testing if the user clicks heart, it aves in favorite database
def test_save_favorite_integration(client):
    response = client.post('/save_favorite', json={
        'activity': 'Watch a documentary.',
        'weather_condition': 'Sunny'
    })
    assert response.status_code == 200
    with app.app_context():
        saved_item = Favorite.query.first()
        assert saved_item is not None
        assert saved_item.activity_text == 'Watch a documentary.'