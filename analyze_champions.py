#!/usr/bin/env python3
"""
Analyze former UFC champions' records after losing their belt.
"""

import pandas as pd
import json
from datetime import datetime
import os

def load_data():
    """Load all relevant UFC data files."""
    data = {}
    
    # Load large dataset with fight details
    if os.path.exists('data/large_dataset.csv'):
        print("Loading large dataset...")
        data['fights'] = pd.read_csv('data/large_dataset.csv')
        print(f"Loaded {len(data['fights'])} fights from large dataset")
    
    # Load medium dataset as backup
    if os.path.exists('data/medium_dataset.csv'):
        print("Loading medium dataset...")
        data['medium_fights'] = pd.read_csv('data/medium_dataset.csv')
        print(f"Loaded {len(data['medium_fights'])} fights from medium dataset")
    
    # Load fighter info
    if os.path.exists('data/fighters.csv'):
        print("Loading fighters data...")
        data['fighters'] = pd.read_csv('data/fighters.csv')
        print(f"Loaded {len(data['fighters'])} fighters")
    
    # Load events
    if os.path.exists('data/events.csv'):
        print("Loading events data...")
        data['events'] = pd.read_csv('data/events.csv')
        print(f"Loaded {len(data['events'])} events")
    
    # Load existing champions records
    if os.path.exists('data/champions_records.json'):
        print("Loading existing champions records...")
        with open('data/champions_records.json', 'r') as f:
            data['existing_records'] = json.load(f)
    
    return data

def identify_title_fights(fights_df):
    """Identify title fights from the dataset."""
    title_fights = []
    
    if 'is_title_bout' in fights_df.columns:
        # Filter for title fights
        title_mask = fights_df['is_title_bout'] == 1
        title_fights = fights_df[title_mask].copy()
    else:
        # Look for championship indicators in event names or methods
        championship_keywords = ['title', 'championship', 'champion', 'belt', 'vacant']
        
        title_mask = fights_df['event_name'].str.contains('|'.join(championship_keywords), case=False, na=False)
        title_fights = fights_df[title_mask].copy()
    
    return title_fights

def parse_fight_date(fight_row):
    """Parse fight date from various formats."""
    if 'date' in fight_row and pd.notna(fight_row['date']):
        return pd.to_datetime(fight_row['date'])
    elif 'event_name' in fight_row:
        # Try to extract date from event name or use a lookup
        event_name = fight_row['event_name']
        # This would need event date mapping
        return None
    return None

def find_champion_losses(fights_df):
    """Find fights where champions lost their titles."""
    champion_losses = []
    
    # Look for known former champions
    known_champions = [
        'Anderson Silva', 'Conor McGregor', 'Ronda Rousey', 'Jon Jones',
        'Daniel Cormier', 'Stipe Miocic', 'Amanda Nunes', 'Jose Aldo',
        'Dominick Cruz', 'T.J. Dillashaw', 'Henry Cejudo', 'Max Holloway',
        'Rafael dos Anjos', 'Eddie Alvarez', 'Robbie Lawler', 'Tyron Woodley',
        'Luke Rockhold', 'Michael Bisping', 'Chris Weidman', 'Fabricio Werdum',
        'Cain Velasquez', 'Junior dos Santos', 'Brock Lesnar', 'Frank Mir',
        'Chuck Liddell', 'Tito Ortiz', 'Matt Hughes', 'B.J. Penn',
        'Sean Sherk', 'Jens Pulver', 'Tim Sylvia', 'Andrei Arlovski',
        'Rich Franklin', 'Evan Tanner', 'Dave Menne', 'Murilo Bustamante',
        'Carlos Newton', 'Pat Miletich', 'Maurice Smith', 'Randy Couture',
        'Vitor Belfort', 'Ken Shamrock', 'Dan Severn', 'Mark Coleman',
        'Don Frye', 'Mark Kerr', 'Pete Williams', 'Bas Rutten',
        'Kevin Randleman', 'Tedd Williams', 'Evan Tanner', 'Yuki Nakai'
    ]
    
    for champion in known_champions:
        # Find fights where this champion fought
        champion_fights = fights_df[
            (fights_df['r_fighter'].str.contains(champion, case=False, na=False)) |
            (fights_df['b_fighter'].str.contains(champion, case=False, na=False))
        ].copy()
        
        # Sort by date/event order
        champion_fights = champion_fights.sort_values(['event_name'])
        
        # Look for losses that could be title losses
        for idx, fight in champion_fights.iterrows():
            is_red = champion.lower() in str(fight['r_fighter']).lower()
            is_blue = champion.lower() in str(fight['b_fighter']).lower()
            
            if is_red and fight['winner'] == 'Blue':
                champion_losses.append({
                    'champion': champion,
                    'event': fight['event_name'],
                    'opponent': fight['b_fighter'],
                    'method': fight.get('method', 'Unknown'),
                    'weight_class': fight.get('weight_class', 'Unknown'),
                    'fight_data': fight
                })
            elif is_blue and fight['winner'] == 'Red':
                champion_losses.append({
                    'champion': champion,
                    'event': fight['event_name'],
                    'opponent': fight['r_fighter'],
                    'method': fight.get('method', 'Unknown'),
                    'weight_class': fight.get('weight_class', 'Unknown'),
                    'fight_data': fight
                })
    
    return champion_losses

def calculate_post_title_loss_record(champion_name, title_loss_event, fights_df):
    """Calculate a champion's record after losing their title."""
    
    # Find all fights for this champion
    champion_fights = fights_df[
        (fights_df['r_fighter'].str.contains(champion_name, case=False, na=False)) |
        (fights_df['b_fighter'].str.contains(champion_name, case=False, na=False))
    ].copy()
    
    # Sort fights chronologically (this is approximate based on event names)
    champion_fights = champion_fights.sort_values(['event_name'])
    
    # Find the title loss fight index
    title_loss_idx = None
    for idx, fight in champion_fights.iterrows():
        if title_loss_event.lower() in fight['event_name'].lower():
            title_loss_idx = idx
            break
    
    if title_loss_idx is None:
        return None
    
    # Get fights after the title loss
    post_loss_fights = champion_fights[champion_fights.index > title_loss_idx]
    
    wins = 0
    losses = 0
    draws = 0
    
    for idx, fight in post_loss_fights.iterrows():
        is_red = champion_name.lower() in str(fight['r_fighter']).lower()
        is_blue = champion_name.lower() in str(fight['b_fighter']).lower()
        
        if is_red:
            if fight['winner'] == 'Red':
                wins += 1
            elif fight['winner'] == 'Blue':
                losses += 1
            elif fight['winner'] in ['Draw', 'No Contest']:
                draws += 1
        elif is_blue:
            if fight['winner'] == 'Blue':
                wins += 1
            elif fight['winner'] == 'Red':
                losses += 1
            elif fight['winner'] in ['Draw', 'No Contest']:
                draws += 1
    
    return {
        'wins': wins,
        'losses': losses,
        'draws': draws,
        'total_fights': len(post_loss_fights),
        'record_string': f"{wins}-{losses}" + (f"-{draws}" if draws > 0 else "")
    }

def analyze_known_champions(fights_df):
    """Analyze known former champions and their post-title loss records."""
    
    # Known title loss events for major champions
    known_title_losses = {
        'Anderson Silva': 'UFC 162',  # Lost to Chris Weidman
        'Conor McGregor': 'UFC 196',  # Lost to Nate Diaz (not title fight, but first major loss)
        'Ronda Rousey': 'UFC 193',   # Lost to Holly Holm
        'Jon Jones': 'UFC 214',      # DQ vs Hamill, but also consider DC fights
        'Jose Aldo': 'UFC 194',      # Lost to McGregor
        'Dominick Cruz': 'UFC 207',  # Lost to Cody Garbrandt
        'Luke Rockhold': 'UFC 199',  # Lost to Bisping
        'Michael Bisping': 'UFC 217', # Lost to GSP
        'Chris Weidman': 'UFC 194',  # Lost to Rockhold
        'Fabricio Werdum': 'UFC 198', # Lost to Stipe
        'Cain Velasquez': 'UFC 188', # Lost to Werdum
        'T.J. Dillashaw': 'UFC 217', # Lost to Cody
        'Max Holloway': 'UFC 245',   # Lost to Volkanovski
        'Tyron Woodley': 'UFC 235',  # Lost to Usman
        'Robbie Lawler': 'UFC 201',  # Lost to Woodley
        'Rafael dos Anjos': 'UFC 196', # Lost to Eddie Alvarez
    }
    
    results = []
    
    for champion, title_loss_event in known_title_losses.items():
        record = calculate_post_title_loss_record(champion, title_loss_event, fights_df)
        if record:
            results.append({
                'name': champion,
                'title_loss_event': title_loss_event,
                'post_loss_record': record['record_string'],
                'detailed_record': record
            })
            print(f"{champion}: {record['record_string']} after losing title at {title_loss_event}")
    
    return results

def main():
    """Main analysis function."""
    print("=== UFC Former Champions Analysis ===")
    print("Loading data...")
    
    data = load_data()
    
    if 'fights' in data:
        fights_df = data['fights']
    elif 'medium_fights' in data:
        fights_df = data['medium_fights']
    else:
        print("No fight data found!")
        return
    
    print(f"\nAnalyzing {len(fights_df)} fights...")
    
    # Identify title fights
    title_fights = identify_title_fights(fights_df)
    print(f"Found {len(title_fights)} potential title fights")
    
    # Find champion losses
    champion_losses = find_champion_losses(fights_df)
    print(f"Found {len(champion_losses)} potential champion losses")
    
    # Analyze known champions
    print("\n=== Former Champions' Records After Losing Title ===")
    champion_records = analyze_known_champions(fights_df)
    
    # Save results
    output = {
        'analysis_date': datetime.now().isoformat(),
        'total_fights_analyzed': len(fights_df),
        'title_fights_found': len(title_fights),
        'champion_records': champion_records
    }
    
    with open('former_champions_analysis.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\nAnalysis complete! Results saved to former_champions_analysis.json")
    print(f"Analyzed {len(champion_records)} former champions")

if __name__ == '__main__':
    main() 