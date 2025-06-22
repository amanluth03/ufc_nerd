from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

app = Flask(__name__)
CORS(app)

# Load the comprehensive datasets
try:
    events_df = pd.read_csv('../data/events.csv')
    fighters_df = pd.read_csv('../data/fighters.csv')
    fights_df = pd.read_csv('../data/fights.csv')
    
    # Also load the UFC master dataset for championship analysis
    ufc_master_df = pd.read_csv('../data/ufc-master.csv')
    
    # Load the corrected champions records
    with open('../data/champions_records.json', 'r') as f:
        corrected_champions = json.load(f)
    
    # Convert dates
    events_df['date'] = pd.to_datetime(events_df['date'])
    fighters_df['birthdate'] = pd.to_datetime(fighters_df['birthdate'], errors='coerce')
    
    print(f"Loaded {len(events_df)} events, {len(fighters_df)} fighters, {len(fights_df)} fights")
    print(f"Loaded {len(ufc_master_df)} historical fights for championship analysis")
    print(f"Loaded {len(corrected_champions)} corrected former champions records")
    
except Exception as e:
    print(f"Error loading data: {e}")
    # Create empty DataFrames as fallback
    events_df = pd.DataFrame()
    fighters_df = pd.DataFrame()
    fights_df = pd.DataFrame()
    ufc_master_df = pd.DataFrame()
    corrected_champions = []

# Calculate fighter ages
current_date = datetime.now()
fighters_df['age'] = fighters_df['birthdate'].apply(
    lambda x: (current_date - x).days // 365 if pd.notna(x) else None
)

def calculate_fighter_age(birthdate):
    """Calculate fighter age"""
    if pd.isna(birthdate):
        return None
    return (datetime.now() - birthdate).days // 365

def get_fighter_performance_metrics():
    """Calculate comprehensive fighter performance metrics"""
    # Merge fights with fighter data
    fights_with_winners = fights_df.merge(
        fighters_df[['fighter_id', 'name', 'wins', 'losses', 'draws', 'country', 'weight (lbs)', 'height (cm)']],
        left_on='winner', right_on='fighter_id', how='left'
    )
    
    # Calculate win rates and performance metrics
    fighter_stats = []
    
    for _, fighter in fighters_df.iterrows():
        total_fights = fighter['wins'] + fighter['losses'] + fighter['draws']
        if total_fights > 0:
            win_rate = (fighter['wins'] / total_fights) * 100
            
            # Get fights for this fighter
            fighter_fights = fights_df[
                (fights_df['left_fighter_id'] == fighter['fighter_id']) |
                (fights_df['right_fighter_id'] == fighter['fighter_id'])
            ]
            
            # Calculate finish rate
            ko_tko_rate = ((fighter['wins_by_ko_tko'] or 0) / fighter['wins']) * 100 if fighter['wins'] > 0 else 0
            sub_rate = ((fighter['wins_by_submission'] or 0) / fighter['wins']) * 100 if fighter['wins'] > 0 else 0
            finish_rate = ko_tko_rate + sub_rate
            
            # Age calculation
            age = calculate_fighter_age(fighter['birthdate']) if pd.notna(fighter['birthdate']) else None
            
            # Performance category
            if win_rate >= 80 and total_fights >= 10:
                category = "Elite"
            elif win_rate >= 70 and total_fights >= 8:
                category = "High-Level"
            elif win_rate >= 60 and total_fights >= 5:
                category = "Solid"
            elif win_rate >= 50:
                category = "Developing"
            else:
                category = "Struggling"
            
            fighter_stats.append({
                'fighter_id': fighter['fighter_id'],
                'name': fighter['name'],
                'wins': int(fighter['wins']) if pd.notna(fighter['wins']) else 0,
                'losses': int(fighter['losses']) if pd.notna(fighter['losses']) else 0,
                'draws': int(fighter['draws']) if pd.notna(fighter['draws']) else 0,
                'total_fights': total_fights,
                'win_rate': round(win_rate, 1),
                'finish_rate': round(finish_rate, 1),
                'ko_tko_wins': int(fighter['wins_by_ko_tko']) if pd.notna(fighter['wins_by_ko_tko']) else 0,
                'submission_wins': int(fighter['wins_by_submission']) if pd.notna(fighter['wins_by_submission']) else 0,
                'country': fighter['country'],
                'weight_lbs': fighter['weight (lbs)'] if pd.notna(fighter['weight (lbs)']) else None,
                'height_cm': fighter['height (cm)'] if pd.notna(fighter['height (cm)']) else None,
                'age': age,
                'category': category,
                'recent_fights': len(fighter_fights)
            })
    
    return sorted(fighter_stats, key=lambda x: x['win_rate'], reverse=True)

def analyze_fight_outcomes():
    """Analyze fight outcome patterns and methods"""
    outcomes = {}
    
    # Count finish methods
    method_counts = fights_df['method'].value_counts().head(10) if 'method' in fights_df.columns else pd.Series()
    
    # Round analysis
    round_analysis = {}
    if 'round' in fights_df.columns:
        round_counts = fights_df['round'].value_counts().sort_index()
        round_analysis = {
            'most_common_round': int(round_counts.index[0]) if len(round_counts) > 0 else 1,
            'round_distribution': round_counts.to_dict()
        }
    
    # Weight class analysis
    weight_class_fights = {}
    if 'weight_class' in fights_df.columns:
        weight_class_fights = fights_df['weight_class'].value_counts().head(10).to_dict()
    
    return {
        'total_fights': len(fights_df),
        'finish_methods': method_counts.to_dict(),
        'round_analysis': round_analysis,
        'weight_class_distribution': weight_class_fights
    }

def get_recent_events_analysis():
    """Analyze recent UFC events and trends"""
    if events_df.empty:
        return {}
    
    # Sort by date and get recent events
    recent_events = events_df.sort_values('date', ascending=False).head(20)
    
    # Event frequency analysis
    events_by_year = events_df.groupby(events_df['date'].dt.year).size().to_dict()
    
    # Location analysis
    locations = events_df['location'].str.extract(r'([^,]+)$')[0].value_counts().head(10) if 'location' in events_df.columns else pd.Series()
    
    return {
        'total_events': len(events_df),
        'recent_events': [
            {
                'title': event['title'],
                'date': event['date'].strftime('%Y-%m-%d'),
                'location': event['location']
            } for _, event in recent_events.iterrows()
        ],
        'events_by_year': events_by_year,
        'top_locations': locations.to_dict()
    }

def identify_rising_stars():
    """Identify rising stars and prospects in UFC"""
    fighter_stats = get_fighter_performance_metrics()
    
    # Filter for potential rising stars (young, high win rate, active)
    rising_stars = [
        fighter for fighter in fighter_stats
        if fighter['age'] and fighter['age'] <= 28
        and fighter['win_rate'] >= 75
        and fighter['total_fights'] >= 5
        and fighter['total_fights'] <= 15
    ]
    
    return sorted(rising_stars, key=lambda x: (x['win_rate'], x['finish_rate']), reverse=True)[:10]

def analyze_international_representation():
    """Analyze international representation in UFC"""
    if fighters_df.empty:
        return {}
    
    country_stats = fighters_df['country'].value_counts().head(15)
    
    # Calculate average performance by country (for countries with 10+ fighters)
    country_performance = []
    for country in country_stats.index:
        if country_stats[country] >= 10:
            country_fighters = fighters_df[fighters_df['country'] == country]
            
            # Calculate average stats
            total_fights = country_fighters['wins'] + country_fighters['losses'] + country_fighters['draws']
            avg_win_rate = (country_fighters['wins'].sum() / total_fights.sum()) * 100 if total_fights.sum() > 0 else 0
            
            country_performance.append({
                'country': country,
                'fighter_count': int(country_stats[country]),
                'avg_win_rate': round(avg_win_rate, 1),
                'total_wins': int(country_fighters['wins'].sum()),
                'total_fights': int(total_fights.sum())
            })
    
    return {
        'country_distribution': country_stats.to_dict(),
        'country_performance': sorted(country_performance, key=lambda x: x['avg_win_rate'], reverse=True)
    }

def get_database_stats():
    """Get basic database statistics"""
    return {
        'total_fighters': len(fighters_df),
        'total_events': len(events_df),
        'total_fights': len(fights_df),
        'historical_fights': len(ufc_master_df) if not ufc_master_df.empty else 0
    }

def get_performance_summary():
    """Get performance summary across all fighters"""
    if fighters_df.empty:
        return {}
    
    # Calculate win rates
    fighters_df['total_fights'] = fighters_df['wins'] + fighters_df['losses'] + fighters_df['draws']
    active_fighters = fighters_df[fighters_df['total_fights'] >= 3]
    
    if active_fighters.empty:
        return {}
    
    active_fighters['win_rate'] = (active_fighters['wins'] / active_fighters['total_fights'] * 100).round(1)
    
    # Categorize fighters
    categories = {
        'Elite (80%+)': len(active_fighters[active_fighters['win_rate'] >= 80]),
        'Very Good (70-79%)': len(active_fighters[(active_fighters['win_rate'] >= 70) & (active_fighters['win_rate'] < 80)]),
        'Good (60-69%)': len(active_fighters[(active_fighters['win_rate'] >= 60) & (active_fighters['win_rate'] < 70)]),
        'Average (50-59%)': len(active_fighters[(active_fighters['win_rate'] >= 50) & (active_fighters['win_rate'] < 60)]),
        'Below Average (<50%)': len(active_fighters[active_fighters['win_rate'] < 50])
    }
    
    return {
        'fighter_categories': categories,
        'average_win_rate': active_fighters['win_rate'].mean().round(1),
        'total_active_fighters': len(active_fighters)
    }

def get_data_coverage():
    """Get data coverage information"""
    if events_df.empty:
        return {}
    
    earliest_event = events_df['date'].min().strftime('%Y-%m-%d')
    latest_event = events_df['date'].max().strftime('%Y-%m-%d')
    span_years = (events_df['date'].max() - events_df['date'].min()).days // 365
    
    return {
        'earliest_event': earliest_event,
        'latest_event': latest_event,
        'events_span_years': span_years
    }

# Former Champions Analysis Functions (using ufc-master.csv)
def identify_former_champions():
    """Identify former champions from the UFC master dataset"""
    if ufc_master_df.empty:
        return {}
    
    # Filter for title bouts
    title_bouts = ufc_master_df[ufc_master_df['TitleBout'] == True].copy()
    
    if title_bouts.empty:
        return {}
    
    # Convert date column
    title_bouts['Date'] = pd.to_datetime(title_bouts['Date'])
    title_bouts = title_bouts.sort_values('Date')
    
    # Track championship lineage by weight class
    champions_by_weight = {}
    former_champions = {}
    
    for _, fight in title_bouts.iterrows():
        weight_class = fight['WeightClass']
        red_fighter = fight['RedFighter']
        blue_fighter = fight['BlueFighter']
        winner = fight['Winner']
        
        # Determine winner name
        if winner == 'Red':
            winner_name = red_fighter
            loser_name = blue_fighter
        elif winner == 'Blue':
            winner_name = blue_fighter
            loser_name = red_fighter
        else:
            continue
        
        # Check if this is a title change
        current_champion = champions_by_weight.get(weight_class)
        
        if current_champion and current_champion != winner_name:
            # Previous champion lost their belt
            if current_champion not in former_champions:
                former_champions[current_champion] = {
                    'name': current_champion,
                    'weight_class': weight_class,
                    'lost_belt_date': fight['Date'].strftime('%Y-%m-%d'),
                    'lost_to': winner_name,
                    'fights_after_loss': []
                }
        
        # Update current champion
        champions_by_weight[weight_class] = winner_name
    
    return former_champions

def calculate_post_belt_records():
    """Calculate fight records after losing championship belt"""
    former_champions = identify_former_champions()
    
    if not former_champions or ufc_master_df.empty:
        return []
    
    ufc_master_df['Date'] = pd.to_datetime(ufc_master_df['Date'])
    
    for champion_name, champion_data in former_champions.items():
        lost_belt_date = pd.to_datetime(champion_data['lost_belt_date'])
        
        # Find all fights after losing the belt
        post_belt_fights = ufc_master_df[
            (ufc_master_df['Date'] > lost_belt_date) &
            ((ufc_master_df['RedFighter'] == champion_name) | 
             (ufc_master_df['BlueFighter'] == champion_name))
        ].copy()
        
        wins = 0
        losses = 0
        
        for _, fight in post_belt_fights.iterrows():
            if fight['RedFighter'] == champion_name:
                if fight['Winner'] == 'Red':
                    wins += 1
                elif fight['Winner'] == 'Blue':
                    losses += 1
            elif fight['BlueFighter'] == champion_name:
                if fight['Winner'] == 'Blue':
                    wins += 1
                elif fight['Winner'] == 'Red':
                    losses += 1
        
        # Update champion data
        champion_data['wins_after_belt_loss'] = wins
        champion_data['losses_after_belt_loss'] = losses
        champion_data['total_fights_after_belt_loss'] = wins + losses
        champion_data['record_after_belt_loss'] = f"{wins}-{losses}"
        
        if (wins + losses) > 0:
            champion_data['win_percentage_after_belt_loss'] = round((wins / (wins + losses)) * 100, 1)
        else:
            champion_data['win_percentage_after_belt_loss'] = 0
    
    # Convert to list and sort by win percentage
    champions_list = list(former_champions.values())
    champions_list = sorted(champions_list, key=lambda x: x['win_percentage_after_belt_loss'], reverse=True)
    
    return champions_list

def get_former_champions_summary():
    """Get summary statistics for former champions"""
    champions = calculate_post_belt_records()
    
    if not champions:
        return {}
    
    total_champions = len(champions)
    total_wins = sum(c['wins_after_belt_loss'] for c in champions)
    total_losses = sum(c['losses_after_belt_loss'] for c in champions)
    total_fights = sum(c['total_fights_after_belt_loss'] for c in champions)
    
    overall_win_percentage = round((total_wins / total_fights) * 100, 1) if total_fights > 0 else 0
    avg_fights_per_champion = round(total_fights / total_champions, 1) if total_champions > 0 else 0
    
    # Performance breakdown
    elite_performers = [c for c in champions if c['win_percentage_after_belt_loss'] >= 70]
    good_performers = [c for c in champions if 50 <= c['win_percentage_after_belt_loss'] < 70]
    struggling_performers = [c for c in champions if c['win_percentage_after_belt_loss'] < 50]
    
    return {
        'total_former_champions': total_champions,
        'total_wins_after_belt_loss': total_wins,
        'total_losses_after_belt_loss': total_losses,
        'overall_win_percentage_after_belt_loss': overall_win_percentage,
        'average_fights_per_former_champion': avg_fights_per_champion,
        'performance_breakdown': {
            'elite_performers': {
                'count': len(elite_performers),
                'percentage': round((len(elite_performers) / total_champions) * 100, 1),
                'criteria': '70%+ win rate'
            },
            'good_performers': {
                'count': len(good_performers),
                'percentage': round((len(good_performers) / total_champions) * 100, 1),
                'criteria': '50-69% win rate'
            },
            'struggling_performers': {
                'count': len(struggling_performers),
                'percentage': round((len(struggling_performers) / total_champions) * 100, 1),
                'criteria': '<50% win rate'
            }
        }
    }

@app.route('/api/overview', methods=['GET'])
def get_overview():
    """Get comprehensive UFC database overview"""
    try:
        fighter_stats = get_fighter_performance_metrics()
        fight_outcomes = analyze_fight_outcomes()
        
        # Calculate summary statistics
        total_fights_all = sum(f['total_fights'] for f in fighter_stats)
        avg_win_rate = np.mean([f['win_rate'] for f in fighter_stats if f['total_fights'] >= 3])
        
        # Category distribution
        category_dist = {}
        for fighter in fighter_stats:
            cat = fighter['category']
            category_dist[cat] = category_dist.get(cat, 0) + 1
        
        return jsonify({
            'database_stats': get_database_stats(),
            'performance_summary': get_performance_summary(),
            'fight_analysis': fight_outcomes,
            'data_coverage': get_data_coverage()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fighters/top-performers', methods=['GET'])
def get_top_performers():
    """Get top performing fighters across different metrics"""
    try:
        fighter_stats = get_fighter_performance_metrics()
        
        # Filter for fighters with meaningful sample size
        qualified_fighters = [f for f in fighter_stats if f['total_fights'] >= 5]
        
        return jsonify({
            'by_win_rate': qualified_fighters[:20],
            'by_finish_rate': sorted(qualified_fighters, key=lambda x: x['finish_rate'], reverse=True)[:15],
            'most_active': sorted(qualified_fighters, key=lambda x: x['total_fights'], reverse=True)[:15],
            'rising_stars': identify_rising_stars()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/international', methods=['GET'])
def get_international_analytics():
    """Get international representation and performance analytics"""
    try:
        return jsonify(analyze_international_representation())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events/analysis', methods=['GET'])
def get_events_analysis():
    """Get comprehensive events analysis"""
    try:
        return jsonify(get_recent_events_analysis())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fighters/search/<name>', methods=['GET'])
def search_fighter(name):
    """Search for fighters by name"""
    try:
        # Case-insensitive search
        matching_fighters = fighters_df[
            fighters_df['name'].str.contains(name, case=False, na=False)
        ].head(10)
        
        results = []
        for _, fighter in matching_fighters.iterrows():
            total_fights = fighter['wins'] + fighter['losses'] + fighter['draws']
            win_rate = (fighter['wins'] / total_fights * 100) if total_fights > 0 else 0
            
            results.append({
                'fighter_id': fighter.get('fighter_id', 'N/A'),
                'name': fighter['name'],
                'record': f"{fighter['wins']}-{fighter['losses']}-{fighter['draws']}",
                'win_rate': round(win_rate, 1),
                'country': fighter.get('nationality', 'Unknown'),
                'weight_lbs': fighter.get('weight_lbs', None)
            })
        
        return jsonify({
            'query': name,
            'total_found': len(results),
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/advanced', methods=['GET'])
def get_advanced_analytics():
    """Get advanced UFC analytics and insights"""
    try:
        fighter_stats = get_fighter_performance_metrics()
        
        # Age analysis
        fighters_with_age = [f for f in fighter_stats if f['age']]
        if fighters_with_age:
            avg_age = np.mean([f['age'] for f in fighters_with_age])
            age_performance = {}
            
            for age_group in ['20-25', '26-30', '31-35', '36+']:
                if age_group == '20-25':
                    group_fighters = [f for f in fighters_with_age if 20 <= f['age'] <= 25]
                elif age_group == '26-30':
                    group_fighters = [f for f in fighters_with_age if 26 <= f['age'] <= 30]
                elif age_group == '31-35':
                    group_fighters = [f for f in fighters_with_age if 31 <= f['age'] <= 35]
                else:
                    group_fighters = [f for f in fighters_with_age if f['age'] >= 36]
                
                if group_fighters:
                    age_performance[age_group] = {
                        'count': len(group_fighters),
                        'avg_win_rate': round(np.mean([f['win_rate'] for f in group_fighters]), 1)
                    }
        
        # Weight class performance
        weight_performance = {}
        weight_ranges = {
            'Flyweight': (0, 130),
            'Bantamweight': (130, 140),
            'Featherweight': (140, 150),
            'Lightweight': (150, 160),
            'Welterweight': (160, 180),
            'Middleweight': (180, 200),
            'Light Heavyweight': (200, 220),
            'Heavyweight': (220, 300)
        }
        
        for weight_class, (min_w, max_w) in weight_ranges.items():
            class_fighters = [
                f for f in fighter_stats 
                if f['weight_lbs'] and min_w < f['weight_lbs'] <= max_w and f['total_fights'] >= 3
            ]
            
            if class_fighters:
                weight_performance[weight_class] = {
                    'fighter_count': len(class_fighters),
                    'avg_win_rate': round(np.mean([f['win_rate'] for f in class_fighters]), 1),
                    'avg_finish_rate': round(np.mean([f['finish_rate'] for f in class_fighters]), 1)
                }
        
        return jsonify({
            'age_analytics': {
                'average_age': round(avg_age, 1) if fighters_with_age else None,
                'age_group_performance': age_performance if fighters_with_age else {}
            },
            'weight_class_analytics': weight_performance,
            'elite_fighters': [f for f in fighter_stats if f['category'] == 'Elite'][:10],
            'performance_trends': {
                'high_finishers': sorted(fighter_stats, key=lambda x: x['finish_rate'], reverse=True)[:10],
                'volume_fighters': sorted(fighter_stats, key=lambda x: x['total_fights'], reverse=True)[:10]
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'data_loaded': not (events_df.empty or fighters_df.empty or fights_df.empty or ufc_master_df.empty),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/former-champions/analysis', methods=['GET'])
def get_former_champions_analysis():
    """Get complete former champions analysis using corrected data"""
    try:
        # Use the corrected champions data instead of calculating dynamically
        champions = []
        
        for champion in corrected_champions:
            # Parse the record string (e.g., "5-4" -> wins=5, losses=4)
            record_parts = champion['record_after_belt'].split('-')
            wins = int(record_parts[0])
            losses = int(record_parts[1])
            total_fights = wins + losses
            
            champions.append({
                'name': champion['name'],
                'record_after_belt_loss': champion['record_after_belt'],
                'wins_after_belt_loss': wins,
                'losses_after_belt_loss': losses,
                'total_fights_after_belt_loss': total_fights,
                'win_percentage_after_belt_loss': champion['win_percentage'],
                'weight_class': champion.get('weight_class', 'Unknown'),
                'lost_to': champion.get('lost_to', 'Unknown'),
                'lost_belt_date': champion.get('title_loss_details', '').split(' at ')[-1].split(' (')[-1].replace(')', '') if 'at' in champion.get('title_loss_details', '') else 'Unknown'
            })
        
        # Calculate summary from corrected data
        total_champions = len(champions)
        total_wins = sum(c['wins_after_belt_loss'] for c in champions)
        total_losses = sum(c['losses_after_belt_loss'] for c in champions)
        total_fights = sum(c['total_fights_after_belt_loss'] for c in champions)
        
        overall_win_percentage = round((total_wins / total_fights) * 100, 1) if total_fights > 0 else 0
        
        # Performance breakdown
        elite_performers = [c for c in champions if c['win_percentage_after_belt_loss'] >= 70]
        good_performers = [c for c in champions if 50 <= c['win_percentage_after_belt_loss'] < 70]
        struggling_performers = [c for c in champions if c['win_percentage_after_belt_loss'] < 50]
        
        summary = {
            'total_former_champions': total_champions,
            'total_wins_after_belt_loss': total_wins,
            'total_losses_after_belt_loss': total_losses,
            'overall_win_percentage_after_belt_loss': overall_win_percentage,
            'average_fights_per_former_champion': round(total_fights / total_champions, 1) if total_champions > 0 else 0,
            'performance_breakdown': {
                'elite_performers': {
                    'count': len(elite_performers),
                    'percentage': round((len(elite_performers) / total_champions) * 100, 1),
                    'criteria': '70%+ win rate'
                },
                'good_performers': {
                    'count': len(good_performers),
                    'percentage': round((len(good_performers) / total_champions) * 100, 1),
                    'criteria': '50-69% win rate'
                },
                'struggling_performers': {
                    'count': len(struggling_performers),
                    'percentage': round((len(struggling_performers) / total_champions) * 100, 1),
                    'criteria': '<50% win rate'
                }
            }
        }
        
        return jsonify({
            'former_champions': champions,
            'summary': summary,
            'analysis_note': 'Corrected analysis of UFC champions performance after losing their championship belt',
            'data_source': 'Manually verified and corrected UFC historical records'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/former-champions/summary', methods=['GET'])
def get_former_champions_summary_endpoint():
    """Get summary statistics for former champions"""
    try:
        return jsonify(get_former_champions_summary())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/former-champions/top-performers', methods=['GET'])
def get_former_champions_top_performers():
    """Get top performing former champions"""
    try:
        limit = request.args.get('limit', 15, type=int)
        champions = calculate_post_belt_records()
        
        # Filter out champions with no fights after losing belt
        active_champions = [c for c in champions if c['total_fights_after_belt_loss'] > 0]
        
        return jsonify({
            'top_performers': active_champions[:limit]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dataset/info', methods=['GET'])
def get_dataset_info():
    """Get information about the datasets"""
    try:
        title_bouts = 0
        if not ufc_master_df.empty:
            title_bouts = len(ufc_master_df[ufc_master_df['TitleBout'] == True])
        
        date_range = {}
        if not ufc_master_df.empty:
            ufc_master_df['Date'] = pd.to_datetime(ufc_master_df['Date'])
            date_range = {
                'earliest': ufc_master_df['Date'].min().strftime('%Y-%m-%d'),
                'latest': ufc_master_df['Date'].max().strftime('%Y-%m-%d')
            }
        
        return jsonify({
            'total_fights': len(fights_df),
            'historical_fights': len(ufc_master_df),
            'total_title_bouts': title_bouts,
            'date_range': date_range,
            'modern_dataset': {
                'events': len(events_df),
                'fighters': len(fighters_df),
                'fights': len(fights_df)
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
