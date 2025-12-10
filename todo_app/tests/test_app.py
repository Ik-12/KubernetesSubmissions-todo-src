import pytest
import os
from flask import Flask
from main import TodoApp

def test_default_port():
    app = TodoApp()
    assert app.port == 5000

def test_port_from_env():
    os.environ["PORT"] = "1234"
    app = TodoApp()
    assert app.port == 1234

def test_flask_app_created():
    app = TodoApp()
    assert isinstance(app.flask_app, Flask)

def test_home_route_registered():
    app = TodoApp()
    routes = [rule.rule for rule in app.flask_app.url_map.iter_rules()]
    assert '/' in routes
    
def test_get_home():
    os.environ["PORT"] = "5000"
    app = TodoApp()
    with app.flask_app.test_client() as c:
        response = c.get('/')
        
        assert response.status_code == 200
        assert b"Server started in port 5000" in response.data
