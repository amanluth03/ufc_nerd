import json
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app

def test_get_champion_records():
    client = app.test_client()
    resp = client.get('/api/champions/records')
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert isinstance(data, list)
    assert data
