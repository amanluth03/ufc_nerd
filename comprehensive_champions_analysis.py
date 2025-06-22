#!/usr/bin/env python3
"""
Comprehensive analysis to identify ALL former UFC champions and their records after losing their belt.
"""

import pandas as pd
import json
from datetime import datetime
import os

def load_ufc_data():
    """Load the UFC master dataset."""
    print("Loading UFC master dataset...")
    df = pd.read_csv('data/ufc-master.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"Loaded {len(df)} fights")
    return df

def identify_all_former_champions(df):
    """Identify ALL former champions from the dataset."""
    print("Identifying all former champions...")
    
    # Filter for title bouts
    title_bouts = df[df['TitleBout'] == True].copy()
    title_bouts = title_bouts.sort_values('Date')
    
    print(f"Found {len(title_bouts)} title fights")
    
    # Track championship lineage by weight class
    champions_by_weight = {}
    former_champions = {}
    
    for _, fight in title_bouts.iterrows():
        weight_class = fight['WeightClass']
        red_fighter = fight['RedFighter']
        blue_fighter = fight['BlueFighter']
        winner = fight['Winner']
        date = fight['Date']
        
        # Determine winner and loser
        if winner == 'Red':
            winner_name = red_fighter
            loser_name = blue_fighter
        elif winner == 'Blue':
            winner_name = blue_fighter
            loser_name = red_fighter
        else:
            continue  # Skip draws/no contests
        
        # Check if this is a title change (someone losing their belt)
        current_champion = champions_by_weight.get(weight_class)
        
        if current_champion and current_champion != winner_name:
            # Previous champion lost their belt
            if current_champion not in former_champions:
                former_champions[current_champion] = {
                    'name': current_champion,
                    'weight_class': weight_class,
                    'lost_belt_date': date,
                    'lost_to': winner_name,
                    'title_defenses': 0
                }
        
        # Update current champion
        champions_by_weight[weight_class] = winner_name
    
    print(f"Identified {len(former_champions)} former champions")
    return former_champions

def calculate_post_title_records(df, former_champions):
    """Calculate records for all former champions after losing their title."""
    print("Calculating post-title records...")
    
    results = []
    
    for champion_name, champion_data in former_champions.items():
        lost_belt_date = champion_data['lost_belt_date']
        
        # Find all fights after losing the belt
        post_belt_fights = df[
            (df['Date'] > lost_belt_date) &
            ((df['RedFighter'] == champion_name) | (df['BlueFighter'] == champion_name))
        ].copy()
        
        wins = 0
        losses = 0
        draws = 0
        
        for _, fight in post_belt_fights.iterrows():
            if fight['RedFighter'] == champion_name:
                if fight['Winner'] == 'Red':
                    wins += 1
                elif fight['Winner'] == 'Blue':
                    losses += 1
                else:
                    draws += 1
            elif fight['BlueFighter'] == champion_name:
                if fight['Winner'] == 'Blue':
                    wins += 1
                elif fight['Winner'] == 'Red':
                    losses += 1
                else:
                    draws += 1
        
        total_fights = wins + losses + draws
        win_percentage = round((wins / (wins + losses)) * 100, 1) if (wins + losses) > 0 else 0
        
        # Only include champions who fought after losing their belt
        if total_fights > 0:
            results.append({
                'name': champion_name,
                'weight_class': champion_data['weight_class'],
                'lost_belt_date': lost_belt_date.strftime('%Y-%m-%d'),
                'lost_to': champion_data['lost_to'],
                'record_after_belt': f"{wins}-{losses}" + (f"-{draws}" if draws > 0 else ""),
                'wins_after_belt': wins,
                'losses_after_belt': losses,
                'draws_after_belt': draws,
                'total_fights_after_belt': total_fights,
                'win_percentage': win_percentage,
                'title_loss_details': f"Lost {champion_data['weight_class']} title to {champion_data['lost_to']} on {lost_belt_date.strftime('%B %d, %Y')}"
            })
    
    # Sort by win percentage (descending)
    results.sort(key=lambda x: x['win_percentage'], reverse=True)
    
    print(f"Found {len(results)} former champions with fights after losing their belt")
    return results

def enhance_with_historical_knowledge(champions_list):
    """Enhance the list with additional historical knowledge and corrections."""
    
    # Known corrections and additional details
    enhancements = {
        'Anderson Silva': {
            'notes': 'Longest title reign in UFC history (2,457 days)',
            'legacy_impact': 'Significant decline after losing title'
        },
        'Chuck Liddell': {
            'notes': 'Former Light Heavyweight king',
            'legacy_impact': 'Career ended shortly after title loss'
        },
        'Tito Ortiz': {
            'notes': 'Former Light Heavyweight champion',
            'legacy_impact': 'Had mixed success after losing title'
        },
        'Jose Aldo': {
            'notes': 'Longest featherweight title reign, lost in 13 seconds to McGregor',
            'legacy_impact': 'Showed resilience with even record post-title'
        },
        'Fabricio Werdum': {
            'notes': 'Best post-title record among major champions',
            'legacy_impact': 'Maintained high level after losing heavyweight title'
        }
    }
    
    for champion in champions_list:
        if champion['name'] in enhancements:
            champion.update(enhancements[champion['name']])
    
    return champions_list

def main():
    """Main analysis function."""
    print("=== COMPREHENSIVE UFC FORMER CHAMPIONS ANALYSIS ===\n")
    
    # Load data
    df = load_ufc_data()
    
    # Identify all former champions
    former_champions = identify_all_former_champions(df)
    
    # Calculate their post-title records
    champions_with_records = calculate_post_title_records(df, former_champions)
    
    # Enhance with historical knowledge
    final_champions = enhance_with_historical_knowledge(champions_with_records)
    
    # Save comprehensive results
    with open('all_former_champions.json', 'w') as f:
        json.dump(final_champions, f, indent=2, default=str)
    
    # Print summary
    print(f"\n=== SUMMARY ===")
    print(f"Total former champions with post-title fights: {len(final_champions)}")
    print(f"Weight classes represented: {len(set(c['weight_class'] for c in final_champions))}")
    
    # Top performers
    print(f"\n=== TOP 10 POST-TITLE PERFORMERS ===")
    for i, champion in enumerate(final_champions[:10], 1):
        print(f"{i:2d}. {champion['name']:<20} {champion['record_after_belt']:<8} ({champion['win_percentage']:>5.1f}%) - {champion['weight_class']}")
    
    # Performance breakdown
    elite = [c for c in final_champions if c['win_percentage'] >= 70]
    good = [c for c in final_champions if 50 <= c['win_percentage'] < 70]
    struggling = [c for c in final_champions if c['win_percentage'] < 50]
    
    print(f"\n=== PERFORMANCE BREAKDOWN ===")
    print(f"Elite performers (70%+):     {len(elite):2d} ({len(elite)/len(final_champions)*100:4.1f}%)")
    print(f"Good performers (50-69%):    {len(good):2d} ({len(good)/len(final_champions)*100:4.1f}%)")
    print(f"Struggling performers (<50%): {len(struggling):2d} ({len(struggling)/len(final_champions)*100:4.1f}%)")
    
    print(f"\nResults saved to 'all_former_champions.json'")
    
    return final_champions

if __name__ == "__main__":
    champions = main() 