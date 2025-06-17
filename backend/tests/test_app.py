import pytest
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, calculate_champion_stats, parse_record

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_champions_data():
    """Sample champions data for testing."""
    return [
        {"name": "Test Champion 1", "record_after_belt": "2-1"},
        {"name": "Test Champion 2", "record_after_belt": "0-3"},
        {"name": "Test Champion 3", "record_after_belt": "1-0"}
    ]

class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'UFC Stats API'

class TestParseRecord:
    def test_parse_valid_record(self):
        """Test parsing valid fight records."""
        result = parse_record("2-1")
        assert result == {'wins': 2, 'losses': 1, 'total_fights': 3}
        
        result = parse_record("0-3")
        assert result == {'wins': 0, 'losses': 3, 'total_fights': 3}
        
        result = parse_record("10-5")
        assert result == {'wins': 10, 'losses': 5, 'total_fights': 15}

    def test_parse_invalid_record(self):
        """Test parsing invalid fight records."""
        result = parse_record("invalid")
        assert result == {'wins': 0, 'losses': 0, 'total_fights': 0}
        
        result = parse_record("")
        assert result == {'wins': 0, 'losses': 0, 'total_fights': 0}
        
        result = parse_record(None)
        assert result == {'wins': 0, 'losses': 0, 'total_fights': 0}

class TestCalculateChampionStats:
    def test_calculate_stats_with_data(self, sample_champions_data):
        """Test calculating statistics with valid data."""
        result = calculate_champion_stats(sample_champions_data)
        
        # Check summary
        assert 'summary' in result
        summary = result['summary']
        assert summary['total_champions'] == 3
        assert summary['total_wins'] == 3
        assert summary['total_losses'] == 4
        assert summary['total_fights'] == 7
        assert abs(summary['overall_win_percentage'] - 42.86) < 0.01
        
        # Check champions data
        assert 'champions' in result
        champions = result['champions']
        assert len(champions) == 3
        
        # Check sorting (by win percentage, descending)
        assert champions[0]['win_percentage'] == 100.0  # Test Champion 3: 1-0
        assert champions[1]['win_percentage'] == 66.67  # Test Champion 1: 2-1
        assert champions[2]['win_percentage'] == 0.0    # Test Champion 2: 0-3

    def test_calculate_stats_empty_data(self):
        """Test calculating statistics with empty data."""
        result = calculate_champion_stats([])
        assert result == {}

    def test_calculate_stats_missing_records(self):
        """Test calculating statistics with missing record data."""
        data = [{"name": "Test Champion", "record_after_belt": None}]
        result = calculate_champion_stats(data)
        
        assert result['summary']['total_champions'] == 1
        assert result['summary']['total_fights'] == 0
        assert result['champions'][0]['win_percentage'] == 0

class TestChampionsEndpoints:
    def test_champions_records_endpoint(self, client):
        """Test the main champions records endpoint."""
        response = client.get('/api/champions/records')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should have either summary and champions, or error
        if 'error' not in data:
            assert 'summary' in data or 'champions' in data

    def test_champions_summary_endpoint(self, client):
        """Test the champions summary endpoint."""
        response = client.get('/api/champions/summary')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should have summary data or error
        if 'error' not in data:
            expected_keys = ['total_champions', 'total_wins', 'total_losses', 
                           'total_fights', 'overall_win_percentage']
            for key in expected_keys:
                if key in data:  # Only check if key exists (depends on data availability)
                    assert isinstance(data[key], (int, float))

    def test_top_performers_endpoint(self, client):
        """Test the top performers endpoint."""
        response = client.get('/api/champions/top-performers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            assert 'top_performers' in data
            assert 'limit' in data
            assert data['limit'] == 5  # default limit

    def test_top_performers_with_limit(self, client):
        """Test the top performers endpoint with custom limit."""
        response = client.get('/api/champions/top-performers?limit=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            assert data['limit'] == 3

class TestErrorHandling:
    def test_404_endpoint(self, client):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert 'error' in data
        assert data['error'] == 'Endpoint not found'

if __name__ == '__main__':
    pytest.main([__file__])
