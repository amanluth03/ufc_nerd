import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';
import './App.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const API_BASE_URL = 'http://localhost:5001/api';

function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overviewData, setOverviewData] = useState(null);
  const [topPerformers, setTopPerformers] = useState(null);
  const [internationalData, setInternationalData] = useState(null);
  const [eventsData, setEventsData] = useState(null);
  const [advancedData, setAdvancedData] = useState(null);
  const [formerChampionsData, setFormerChampionsData] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = async (endpoint, setter) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}${endpoint}`);
      setter(response.data);
      setError(null);
    } catch (err) {
      console.error(`Error fetching ${endpoint}:`, err);
      setError(`Failed to load data from ${endpoint}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData('/overview', setOverviewData);
  }, []);

  useEffect(() => {
    if (activeTab === 'performers' && !topPerformers) {
      fetchData('/fighters/top-performers', setTopPerformers);
    } else if (activeTab === 'international' && !internationalData) {
      fetchData('/analytics/international', setInternationalData);
    } else if (activeTab === 'events' && !eventsData) {
      fetchData('/events/analysis', setEventsData);
    } else if (activeTab === 'advanced' && !advancedData) {
      fetchData('/analytics/advanced', setAdvancedData);
    } else if (activeTab === 'former-champions' && !formerChampionsData) {
      fetchData('/former-champions/analysis', setFormerChampionsData);
    }
  }, [activeTab, topPerformers, internationalData, eventsData, advancedData, formerChampionsData]);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/fighters/search/${encodeURIComponent(searchQuery)}`);
      setSearchResults(response.data);
    } catch (err) {
      console.error('Search error:', err);
      setError('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const LoadingSpinner = () => (
    <div className="loading-container">
      <div className="loading-spinner"></div>
      <p>Loading UFC Analytics...</p>
    </div>
  );

  const ErrorMessage = ({ message }) => (
    <div className="error-container">
      <h3>⚠️ Error</h3>
      <p>{message}</p>
    </div>
  );

  const OverviewTab = () => {
    if (!overviewData) return <LoadingSpinner />;

    const categoryChart = {
      labels: Object.keys(overviewData.performance_summary?.fighter_categories || {}),
      datasets: [{
        label: 'Fighter Categories',
        data: Object.values(overviewData.performance_summary?.fighter_categories || {}),
        backgroundColor: [
          '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD'
        ]
      }]
    };

    return (
      <div className="tab-content">
        <div className="overview-header">
          <h2>🥊 UFC Analytics Dashboard</h2>
          <p>Comprehensive analysis of {overviewData.database_stats?.total_fighters} fighters across {overviewData.database_stats?.total_events} events</p>
        </div>

        <div className="stats-grid">
          <div className="stat-card">
            <h3>Total Fighters</h3>
            <div className="stat-number">{overviewData.database_stats?.total_fighters?.toLocaleString()}</div>
            <p>Active competitors</p>
          </div>
          <div className="stat-card">
            <h3>Total Events</h3>
            <div className="stat-number">{overviewData.database_stats?.total_events?.toLocaleString()}</div>
            <p>UFC events covered</p>
          </div>
          <div className="stat-card">
            <h3>Total Fights</h3>
            <div className="stat-number">{overviewData.database_stats?.total_fights?.toLocaleString()}</div>
            <p>Recorded bouts</p>
          </div>
          <div className="stat-card">
            <h3>Average Win Rate</h3>
            <div className="stat-number">{overviewData.performance_summary?.average_win_rate}%</div>
            <p>Across active fighters</p>
          </div>
        </div>

        <div className="data-coverage">
          <h3>📊 Data Coverage</h3>
          <div className="coverage-info">
            <p><strong>Period:</strong> {overviewData.data_coverage?.earliest_event} to {overviewData.data_coverage?.latest_event}</p>
            <p><strong>Span:</strong> {overviewData.data_coverage?.events_span_years} years of UFC history</p>
          </div>
        </div>

        <div className="chart-container">
          <h3>Fighter Performance Categories</h3>
          <div className="chart-wrapper">
            <Pie data={categoryChart} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>

        {overviewData.fight_analysis && (
          <div className="fight-analysis">
            <h3>🥊 Fight Analysis</h3>
            <div className="analysis-grid">
              <div className="analysis-item">
                <h4>Most Common Finish Methods</h4>
                <ul>
                  {Object.entries(overviewData.fight_analysis.finish_methods || {}).slice(0, 5).map(([method, count]) => (
                    <li key={method}>{method}: {count} fights</li>
                  ))}
                </ul>
              </div>
              <div className="analysis-item">
                <h4>Round Distribution</h4>
                {overviewData.fight_analysis.round_analysis && (
                  <p>Most fights end in round {overviewData.fight_analysis.round_analysis.most_common_round}</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    );
  };

  const PerformersTab = () => {
    if (!topPerformers) return <LoadingSpinner />;

    const winRateChart = {
      labels: topPerformers.by_win_rate?.slice(0, 10).map(f => f.name.length > 15 ? f.name.substring(0, 15) + '...' : f.name) || [],
      datasets: [{
        label: 'Win Rate (%)',
        data: topPerformers.by_win_rate?.slice(0, 10).map(f => f.win_rate) || [],
        backgroundColor: '#4ECDC4'
      }]
    };

    return (
      <div className="tab-content">
        <h2>🏆 Top Performers</h2>
        
        <div className="chart-container">
          <h3>Top 10 Fighters by Win Rate</h3>
          <div className="chart-wrapper">
            <Bar data={winRateChart} options={{ 
              responsive: true, 
              maintainAspectRatio: false,
              scales: { y: { beginAtZero: true, max: 100 } }
            }} />
          </div>
        </div>

        <div className="performers-grid">
          <div className="performer-section">
            <h3>🎯 Highest Win Rate (5+ fights)</h3>
            <div className="fighter-list">
              {topPerformers.by_win_rate?.slice(0, 8).map((fighter, index) => (
                <div key={fighter.fighter_id} className="fighter-card">
                  <div className="fighter-rank">#{index + 1}</div>
                  <div className="fighter-info">
                    <h4>{fighter.name}</h4>
                    <p className="record">{fighter.wins}-{fighter.losses}-{fighter.draws}</p>
                    <p className="win-rate">{fighter.win_rate}% win rate</p>
                    <p className="country">{fighter.country}</p>
                  </div>
                  <div className="performance-badge">{fighter.category}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="performer-section">
            <h3>💥 Top Finishers</h3>
            <div className="fighter-list">
              {topPerformers.by_finish_rate?.slice(0, 6).map((fighter, index) => (
                <div key={fighter.fighter_id} className="fighter-card">
                  <div className="fighter-rank">#{index + 1}</div>
                  <div className="fighter-info">
                    <h4>{fighter.name}</h4>
                    <p className="finish-rate">{fighter.finish_rate}% finish rate</p>
                    <p className="finish-breakdown">
                      KO/TKO: {fighter.ko_tko_wins} | Subs: {fighter.submission_wins}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {topPerformers.rising_stars && topPerformers.rising_stars.length > 0 && (
          <div className="rising-stars">
            <h3>🌟 Rising Stars (Age ≤ 28, 75%+ Win Rate)</h3>
            <div className="fighter-list">
              {topPerformers.rising_stars.map((fighter, index) => (
                <div key={fighter.fighter_id} className="fighter-card rising-star">
                  <div className="fighter-info">
                    <h4>{fighter.name}</h4>
                    <p>Age: {fighter.age} | Record: {fighter.wins}-{fighter.losses}-{fighter.draws}</p>
                    <p>Win Rate: {fighter.win_rate}% | Finish Rate: {fighter.finish_rate}%</p>
                    <p className="country">{fighter.country}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const InternationalTab = () => {
    if (!internationalData) return <LoadingSpinner />;

    const countryChart = {
      labels: Object.keys(internationalData.country_distribution || {}).slice(0, 10),
      datasets: [{
        label: 'Number of Fighters',
        data: Object.values(internationalData.country_distribution || {}).slice(0, 10),
        backgroundColor: '#FF6B6B'
      }]
    };

    return (
      <div className="tab-content">
        <h2>🌍 International Representation</h2>
        
        <div className="chart-container">
          <h3>Top 10 Countries by Fighter Count</h3>
          <div className="chart-wrapper">
            <Bar data={countryChart} options={{ responsive: true, maintainAspectRatio: false }} />
          </div>
        </div>

        <div className="international-stats">
          <h3>Country Performance (10+ fighters)</h3>
          <div className="country-performance">
            {internationalData.country_performance?.map((country, index) => (
              <div key={country.country} className="country-card">
                <div className="country-rank">#{index + 1}</div>
                <div className="country-info">
                  <h4>{country.country}</h4>
                  <p>Fighters: {country.fighter_count}</p>
                  <p>Avg Win Rate: {country.avg_win_rate}%</p>
                  <p>Total Record: {country.total_wins}-{country.total_fights - country.total_wins}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const EventsTab = () => {
    if (!eventsData) return <LoadingSpinner />;

    return (
      <div className="tab-content">
        <h2>📅 Events Analysis</h2>
        
        <div className="events-overview">
          <div className="stat-card">
            <h3>Total Events</h3>
            <div className="stat-number">{eventsData.total_events}</div>
          </div>
        </div>

        <div className="events-sections">
          <div className="recent-events">
            <h3>Recent Events</h3>
            <div className="events-list">
              {eventsData.recent_events?.slice(0, 10).map((event, index) => (
                <div key={index} className="event-card">
                  <h4>{event.title}</h4>
                  <p className="event-date">{event.date}</p>
                  <p className="event-location">{event.location}</p>
                </div>
              ))}
            </div>
          </div>

          {eventsData.events_by_year && (
            <div className="events-by-year">
              <h3>Events by Year</h3>
              <div className="year-stats">
                {Object.entries(eventsData.events_by_year).slice(-10).map(([year, count]) => (
                  <div key={year} className="year-item">
                    <span className="year">{year}</span>
                    <span className="count">{count} events</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {eventsData.top_locations && (
            <div className="top-locations">
              <h3>Most Popular Locations</h3>
              <div className="location-list">
                {Object.entries(eventsData.top_locations).slice(0, 8).map(([location, count]) => (
                  <div key={location} className="location-item">
                    <span className="location">{location}</span>
                    <span className="count">{count} events</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const AdvancedTab = () => {
    if (!advancedData) return <LoadingSpinner />;

    return (
      <div className="tab-content">
        <h2>🔬 Advanced Analytics</h2>
        
        <div className="advanced-sections">
          {advancedData.age_analytics?.age_group_performance && (
            <div className="age-analysis">
              <h3>Performance by Age Group</h3>
              <p>Average fighter age: {advancedData.age_analytics.average_age} years</p>
              <div className="age-groups">
                {Object.entries(advancedData.age_analytics.age_group_performance).map(([group, data]) => (
                  <div key={group} className="age-group-card">
                    <h4>{group} years</h4>
                    <p>Fighters: {data.count}</p>
                    <p>Avg Win Rate: {data.avg_win_rate}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {advancedData.weight_class_analytics && (
            <div className="weight-analysis">
              <h3>Weight Class Performance</h3>
              <div className="weight-classes">
                {Object.entries(advancedData.weight_class_analytics).map(([weightClass, data]) => (
                  <div key={weightClass} className="weight-class-card">
                    <h4>{weightClass}</h4>
                    <p>Fighters: {data.fighter_count}</p>
                    <p>Avg Win Rate: {data.avg_win_rate}%</p>
                    <p>Avg Finish Rate: {data.avg_finish_rate}%</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {advancedData.elite_fighters && (
            <div className="elite-fighters">
              <h3>Elite Fighters (80%+ Win Rate, 10+ fights)</h3>
              <div className="fighter-list">
                {advancedData.elite_fighters.slice(0, 6).map((fighter) => (
                  <div key={fighter.fighter_id} className="fighter-card elite">
                    <h4>{fighter.name}</h4>
                    <p>Record: {fighter.wins}-{fighter.losses}-{fighter.draws}</p>
                    <p>Win Rate: {fighter.win_rate}%</p>
                    <p>{fighter.country}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const SearchTab = () => (
    <div className="tab-content">
      <h2>🔍 Fighter Search</h2>
      
      <div className="search-container">
        <div className="search-input-group">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search for fighters (e.g., 'Silva', 'Jon', 'Connor')"
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </div>

      {searchResults && (
        <div className="search-results">
          <h3>Search Results for "{searchResults.query}" ({searchResults.total_found} found)</h3>
          <div className="fighter-list">
            {searchResults.results?.map((fighter) => (
              <div key={fighter.fighter_id} className="fighter-card search-result">
                <div className="fighter-info">
                  <h4>{fighter.name}</h4>
                  <p className="record">Record: {fighter.record}</p>
                  <p className="win-rate">Win Rate: {fighter.win_rate}%</p>
                  <p className="country">{fighter.country}</p>
                  {fighter.weight_lbs && <p className="weight">Weight: {fighter.weight_lbs} lbs</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const FormerChampionsTab = () => {
    if (!formerChampionsData) return <LoadingSpinner />;

    const summary = formerChampionsData.summary;
    const champions = formerChampionsData.former_champions || [];

    const winRateChart = {
      labels: champions.slice(0, 10).map(c => c.name.length > 15 ? c.name.substring(0, 15) + '...' : c.name),
      datasets: [{
        label: 'Win Rate After Belt Loss (%)',
        data: champions.slice(0, 10).map(c => c.win_percentage_after_belt_loss),
        backgroundColor: champions.slice(0, 10).map(c => 
          c.win_percentage_after_belt_loss >= 70 ? '#4caf50' :
          c.win_percentage_after_belt_loss >= 50 ? '#ff9800' : '#f44336'
        )
      }]
    };

    return (
      <div className="tab-content">
        <div className="champions-header">
          <h2>👑 Former UFC Champions Analysis</h2>
          <p>Records after losing their championship belt</p>
          <div className="data-source">
            <small>{formerChampionsData.analysis_note}</small><br/>
            <small>Source: {formerChampionsData.data_source}</small>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="champions-quick-stats">
          <div className="quick-stat-card">
            <h4>Total Former Champions</h4>
            <div className="quick-stat-number">{summary?.total_former_champions || 0}</div>
          </div>
          <div className="quick-stat-card">
            <h4>Combined Record</h4>
            <div className="quick-stat-number">{summary?.total_wins_after_belt_loss || 0}-{summary?.total_losses_after_belt_loss || 0}</div>
          </div>
          <div className="quick-stat-card">
            <h4>Overall Win Rate</h4>
            <div className="quick-stat-number">{summary?.overall_win_percentage_after_belt_loss || 0}%</div>
          </div>
          <div className="quick-stat-card">
            <h4>Elite Performers</h4>
            <div className="quick-stat-number">{summary?.performance_breakdown?.elite_performers?.count || 0}</div>
            <small>70%+ win rate</small>
          </div>
        </div>

        {/* Performance Chart */}
        <div className="chart-container">
          <h3>Top 10 Former Champions - Win Rate After Belt Loss</h3>
          <div className="chart-wrapper">
            <Bar data={winRateChart} options={{ 
              responsive: true, 
              maintainAspectRatio: false,
              scales: { y: { beginAtZero: true, max: 100 } },
              plugins: {
                tooltip: {
                  callbacks: {
                    afterLabel: function(context) {
                      const champion = champions[context.dataIndex];
                      return [
                        `Record: ${champion.record_after_belt_loss}`,
                        `Total fights: ${champion.total_fights_after_belt_loss}`,
                        `Weight class: ${champion.weight_class}`,
                        `Lost belt to: ${champion.lost_to}`
                      ];
                    }
                  }
                }
              }
            }} />
          </div>
        </div>

        {/* Performance Breakdown */}
        {summary?.performance_breakdown && (
          <div className="performance-breakdown">
            <h3>Performance Distribution</h3>
            <div className="performance-summary">
              <div className="performance-item elite">
                <div className="performance-label">Elite Performers (70%+)</div>
                <div className="performance-count">{summary.performance_breakdown.elite_performers.count}</div>
                <div className="performance-percentage">{summary.performance_breakdown.elite_performers.percentage}%</div>
              </div>
              <div className="performance-item good">
                <div className="performance-label">Good Performers (50-69%)</div>
                <div className="performance-count">{summary.performance_breakdown.good_performers.count}</div>
                <div className="performance-percentage">{summary.performance_breakdown.good_performers.percentage}%</div>
              </div>
              <div className="performance-item struggling">
                <div className="performance-label">Struggling (&lt;50%)</div>
                <div className="performance-count">{summary.performance_breakdown.struggling_performers.count}</div>
                <div className="performance-percentage">{summary.performance_breakdown.struggling_performers.percentage}%</div>
              </div>
            </div>
          </div>
        )}

        {/* Champions List */}
        <div className="champions-list">
          <h3>All Former Champions ({champions.length})</h3>
          <div className="fighter-list">
            {champions.map((champion, index) => (
              <div key={index} className="fighter-card champion-card">
                <div className="fighter-rank">#{index + 1}</div>
                <div className="fighter-info">
                  <h4>{champion.name}</h4>
                  <p className="weight-class">{champion.weight_class}</p>
                  <div className="champion-record">
                    <span className="record">{champion.record_after_belt_loss}</span>
                    <span className="win-rate"> ({champion.win_percentage_after_belt_loss}%)</span>
                  </div>
                  <p><strong>Lost belt to:</strong> {champion.lost_to}</p>
                  <p><strong>Date:</strong> {champion.lost_belt_date}</p>
                  <p><strong>Fights after:</strong> {champion.total_fights_after_belt_loss}</p>
                </div>
                <div className={`performance-badge ${
                  champion.win_percentage_after_belt_loss >= 70 ? 'elite' :
                  champion.win_percentage_after_belt_loss >= 50 ? 'good' : 'struggling'
                }`}>
                  {champion.win_percentage_after_belt_loss >= 70 ? 'Elite' :
                   champion.win_percentage_after_belt_loss >= 50 ? 'Good' : 'Struggling'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🥊 UFC Analytics Hub</h1>
        <p>Comprehensive UFC Statistics & Performance Analysis</p>
      </header>

      <nav className="tab-navigation">
        <button 
          className={activeTab === 'overview' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={activeTab === 'former-champions' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('former-champions')}
        >
          👑 Former Champions
        </button>
        <button 
          className={activeTab === 'performers' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('performers')}
        >
          🏆 Top Performers
        </button>
        <button 
          className={activeTab === 'international' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('international')}
        >
          🌍 International
        </button>
        <button 
          className={activeTab === 'events' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('events')}
        >
          📅 Events
        </button>
        <button 
          className={activeTab === 'advanced' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('advanced')}
        >
          🔬 Advanced
        </button>
        <button 
          className={activeTab === 'search' ? 'tab-button active' : 'tab-button'}
          onClick={() => setActiveTab('search')}
        >
          🔍 Search
        </button>
      </nav>

      <main className="app-main">
        {error && <ErrorMessage message={error} />}
        
        {activeTab === 'overview' && <OverviewTab />}
        {activeTab === 'former-champions' && <FormerChampionsTab />}
        {activeTab === 'performers' && <PerformersTab />}
        {activeTab === 'international' && <InternationalTab />}
        {activeTab === 'events' && <EventsTab />}
        {activeTab === 'advanced' && <AdvancedTab />}
        {activeTab === 'search' && <SearchTab />}
      </main>

      <footer className="app-footer">
        <p>UFC Analytics Hub | Powered by comprehensive fight data</p>
      </footer>
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
