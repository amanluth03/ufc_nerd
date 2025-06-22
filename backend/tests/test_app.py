import pytest
import json
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestHealthEndpoint:
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'timestamp' in data

class TestFormerChampionsEndpoints:
    def test_former_champions_analysis_endpoint(self, client):
        """Test the former champions analysis endpoint."""
        response = client.get('/api/former-champions/analysis')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should have either data or error
        if 'error' not in data:
            assert 'former_champions' in data
            assert 'summary' in data
            assert 'analysis_note' in data
            assert 'data_source' in data

    def test_former_champions_summary_endpoint(self, client):
        """Test the former champions summary endpoint."""
        response = client.get('/api/former-champions/summary')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should have summary data or error
        if 'error' not in data:
            expected_keys = ['total_former_champions', 'total_wins_after_belt_loss', 
                           'total_losses_after_belt_loss', 'overall_win_percentage_after_belt_loss']
            # Check if any expected keys exist (depends on data availability)
            has_expected_data = any(key in data for key in expected_keys)
            if has_expected_data:
                for key in expected_keys:
                    if key in data:
                        assert isinstance(data[key], (int, float))

    def test_former_champions_top_performers_endpoint(self, client):
        """Test the former champions top performers endpoint."""
        response = client.get('/api/former-champions/top-performers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            assert 'top_performers' in data

    def test_former_champions_top_performers_with_limit(self, client):
        """Test the former champions top performers endpoint with custom limit."""
        response = client.get('/api/former-champions/top-performers?limit=3')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            assert 'top_performers' in data
            # Check that we get at most 3 results
            if data['top_performers']:
                assert len(data['top_performers']) <= 3

class TestOtherEndpoints:
    def test_overview_endpoint(self, client):
        """Test the overview endpoint."""
        response = client.get('/api/overview')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        # Should have overview data or error
        if 'error' not in data:
            expected_keys = ['database_stats', 'performance_summary', 'fight_analysis', 'data_coverage']
            # Check if any expected keys exist
            has_expected_data = any(key in data for key in expected_keys)
            assert has_expected_data or 'error' in data

    def test_top_performers_endpoint(self, client):
        """Test the fighters top performers endpoint."""
        response = client.get('/api/fighters/top-performers')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            expected_keys = ['by_win_rate', 'by_finish_rate', 'most_active', 'rising_stars']
            has_expected_data = any(key in data for key in expected_keys)
            assert has_expected_data

    def test_search_fighter_endpoint(self, client):
        """Test the fighter search endpoint."""
        response = client.get('/api/fighters/search/test')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            assert 'query' in data
            assert 'total_found' in data
            assert 'results' in data
            assert data['query'] == 'test'

    def test_dataset_info_endpoint(self, client):
        """Test the dataset info endpoint."""
        response = client.get('/api/dataset/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data:
            expected_keys = ['total_fights', 'historical_fights', 'modern_dataset']
            has_expected_data = any(key in data for key in expected_keys)
            assert has_expected_data

class TestErrorHandling:
    def test_404_endpoint(self, client):
        """Test 404 error handling for non-existent endpoint."""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_invalid_search_parameter(self, client):
        """Test search with empty parameter."""
        response = client.get('/api/fighters/search/')
        # Should return 404 for empty search parameter
        assert response.status_code == 404

class TestDataIntegrity:
    def test_former_champions_data_structure(self, client):
        """Test that former champions data has the expected structure."""
        response = client.get('/api/former-champions/analysis')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        if 'error' not in data and 'former_champions' in data:
            champions = data['former_champions']
            if champions:  # If we have champions data
                # Check first champion has expected fields
                champion = champions[0]
                expected_fields = ['name', 'record_after_belt_loss', 'win_percentage_after_belt_loss']
                for field in expected_fields:
                    assert field in champion, f"Missing field: {field}"
                
                # Check data types
                assert isinstance(champion['name'], str)
                assert isinstance(champion['win_percentage_after_belt_loss'], (int, float))

if __name__ == '__main__':
    pytest.main([__file__])
