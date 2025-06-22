#!/usr/bin/env python3
"""
Process complete UFC championship history to identify ALL former champions
and their verified records after losing their titles.
"""

import json
import pandas as pd
from datetime import datetime

def load_ufc_data():
    """Load UFC master dataset."""
    df = pd.read_csv('data/ufc-master.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

def get_former_champions_from_history():
    """
    Extract former champions from the provided championship history.
    This includes all champions who lost their title and fought afterwards.
    """
    
    # Based on the championship history provided, here are the verified former champions
    # who lost their titles and had subsequent fights
    
    former_champions = [
        # Heavyweight
        {"name": "Mark Coleman", "weight_class": "Heavyweight", "lost_to": "Maurice Smith", "lost_date": "1997-07-27"},
        {"name": "Maurice Smith", "weight_class": "Heavyweight", "lost_to": "Randy Couture", "lost_date": "1997-12-21"},
        {"name": "Randy Couture", "weight_class": "Heavyweight", "lost_to": "Josh Barnett", "lost_date": "2002-03-22"},
        {"name": "Ricco Rodriguez", "weight_class": "Heavyweight", "lost_to": "Tim Sylvia", "lost_date": "2003-02-28"},
        {"name": "Tim Sylvia", "weight_class": "Heavyweight", "lost_to": "Frank Mir", "lost_date": "2004-06-19"},
        {"name": "Andrei Arlovski", "weight_class": "Heavyweight", "lost_to": "Tim Sylvia", "lost_date": "2006-04-15"},
        {"name": "Brock Lesnar", "weight_class": "Heavyweight", "lost_to": "Cain Velasquez", "lost_date": "2010-10-23"},
        {"name": "Cain Velasquez", "weight_class": "Heavyweight", "lost_to": "Junior dos Santos", "lost_date": "2011-11-12"},
        {"name": "Junior dos Santos", "weight_class": "Heavyweight", "lost_to": "Cain Velasquez", "lost_date": "2012-12-29"},
        {"name": "Fabricio Werdum", "weight_class": "Heavyweight", "lost_to": "Stipe Miocic", "lost_date": "2016-05-14"},
        {"name": "Stipe Miocic", "weight_class": "Heavyweight", "lost_to": "Daniel Cormier", "lost_date": "2018-07-07"},
        {"name": "Daniel Cormier", "weight_class": "Heavyweight", "lost_to": "Stipe Miocic", "lost_date": "2019-08-17"},
        
        # Light Heavyweight  
        {"name": "Tito Ortiz", "weight_class": "Light Heavyweight", "lost_to": "Randy Couture", "lost_date": "2003-09-26"},
        {"name": "Vitor Belfort", "weight_class": "Light Heavyweight", "lost_to": "Randy Couture", "lost_date": "2004-08-21"},
        {"name": "Chuck Liddell", "weight_class": "Light Heavyweight", "lost_to": "Quinton Jackson", "lost_date": "2007-05-26"},
        {"name": "Quinton Jackson", "weight_class": "Light Heavyweight", "lost_to": "Forrest Griffin", "lost_date": "2008-07-05"},
        {"name": "Forrest Griffin", "weight_class": "Light Heavyweight", "lost_to": "Rashad Evans", "lost_date": "2008-12-27"},
        {"name": "Rashad Evans", "weight_class": "Light Heavyweight", "lost_to": "Lyoto Machida", "lost_date": "2009-05-23"},
        {"name": "Lyoto Machida", "weight_class": "Light Heavyweight", "lost_to": "Mauricio Rua", "lost_date": "2010-05-08"},
        {"name": "Mauricio Rua", "weight_class": "Light Heavyweight", "lost_to": "Jon Jones", "lost_date": "2011-03-19"},
        {"name": "Daniel Cormier", "weight_class": "Light Heavyweight", "lost_to": "Jon Jones", "lost_date": "2018-12-29"},
        {"name": "Jan Blachowicz", "weight_class": "Light Heavyweight", "lost_to": "Glover Teixeira", "lost_date": "2021-10-30"},
        {"name": "Glover Teixeira", "weight_class": "Light Heavyweight", "lost_to": "Jiri Prochazka", "lost_date": "2022-06-12"},
        {"name": "Jamahal Hill", "weight_class": "Light Heavyweight", "lost_to": "Alex Pereira", "lost_date": "2023-11-11"},
        
        # Middleweight
        {"name": "Dave Menne", "weight_class": "Middleweight", "lost_to": "Murilo Bustamante", "lost_date": "2002-01-11"},
        {"name": "Evan Tanner", "weight_class": "Middleweight", "lost_to": "Rich Franklin", "lost_date": "2005-06-04"},
        {"name": "Rich Franklin", "weight_class": "Middleweight", "lost_to": "Anderson Silva", "lost_date": "2006-10-14"},
        {"name": "Anderson Silva", "weight_class": "Middleweight", "lost_to": "Chris Weidman", "lost_date": "2013-07-06"},
        {"name": "Chris Weidman", "weight_class": "Middleweight", "lost_to": "Luke Rockhold", "lost_date": "2015-12-12"},
        {"name": "Luke Rockhold", "weight_class": "Middleweight", "lost_to": "Michael Bisping", "lost_date": "2016-06-04"},
        {"name": "Michael Bisping", "weight_class": "Middleweight", "lost_to": "Georges St-Pierre", "lost_date": "2017-11-04"},
        {"name": "Robert Whittaker", "weight_class": "Middleweight", "lost_to": "Israel Adesanya", "lost_date": "2019-10-06"},
        {"name": "Alex Pereira", "weight_class": "Middleweight", "lost_to": "Israel Adesanya", "lost_date": "2023-04-08"},
        {"name": "Israel Adesanya", "weight_class": "Middleweight", "lost_to": "Sean Strickland", "lost_date": "2023-09-10"},
        {"name": "Sean Strickland", "weight_class": "Middleweight", "lost_to": "Dricus du Plessis", "lost_date": "2024-01-20"},
        
        # Welterweight
        {"name": "Pat Miletich", "weight_class": "Welterweight", "lost_to": "Carlos Newton", "lost_date": "2001-05-04"},
        {"name": "Carlos Newton", "weight_class": "Welterweight", "lost_to": "Matt Hughes", "lost_date": "2001-11-02"},
        {"name": "Matt Hughes", "weight_class": "Welterweight", "lost_to": "B.J. Penn", "lost_date": "2004-01-31"},
        {"name": "B.J. Penn", "weight_class": "Welterweight", "lost_to": "Matt Hughes", "lost_date": "2004-10-22"},
        {"name": "Georges St-Pierre", "weight_class": "Welterweight", "lost_to": "Matt Serra", "lost_date": "2007-04-07"},
        {"name": "Matt Serra", "weight_class": "Welterweight", "lost_to": "Georges St-Pierre", "lost_date": "2008-04-19"},
        {"name": "Johny Hendricks", "weight_class": "Welterweight", "lost_to": "Robbie Lawler", "lost_date": "2014-12-06"},
        {"name": "Robbie Lawler", "weight_class": "Welterweight", "lost_to": "Tyron Woodley", "lost_date": "2016-07-30"},
        {"name": "Tyron Woodley", "weight_class": "Welterweight", "lost_to": "Kamaru Usman", "lost_date": "2019-03-02"},
        {"name": "Kamaru Usman", "weight_class": "Welterweight", "lost_to": "Leon Edwards", "lost_date": "2022-08-20"},
        {"name": "Leon Edwards", "weight_class": "Welterweight", "lost_to": "Belal Muhammad", "lost_date": "2024-07-27"},
        
        # Lightweight
        {"name": "Jens Pulver", "weight_class": "Lightweight", "lost_to": "Sean Sherk", "lost_date": "2006-10-14"},
        {"name": "B.J. Penn", "weight_class": "Lightweight", "lost_to": "Frankie Edgar", "lost_date": "2010-04-10"},
        {"name": "Frankie Edgar", "weight_class": "Lightweight", "lost_to": "Benson Henderson", "lost_date": "2012-02-26"},
        {"name": "Benson Henderson", "weight_class": "Lightweight", "lost_to": "Anthony Pettis", "lost_date": "2013-08-31"},
        {"name": "Anthony Pettis", "weight_class": "Lightweight", "lost_to": "Rafael dos Anjos", "lost_date": "2015-03-14"},
        {"name": "Rafael dos Anjos", "weight_class": "Lightweight", "lost_to": "Eddie Alvarez", "lost_date": "2016-07-07"},
        {"name": "Eddie Alvarez", "weight_class": "Lightweight", "lost_to": "Conor McGregor", "lost_date": "2016-11-12"},
        {"name": "Charles Oliveira", "weight_class": "Lightweight", "lost_to": "Islam Makhachev", "lost_date": "2022-10-22"},
        
        # Featherweight
        {"name": "Jose Aldo", "weight_class": "Featherweight", "lost_to": "Conor McGregor", "lost_date": "2015-12-12"},
        {"name": "Max Holloway", "weight_class": "Featherweight", "lost_to": "Alexander Volkanovski", "lost_date": "2019-12-14"},
        {"name": "Alexander Volkanovski", "weight_class": "Featherweight", "lost_to": "Ilia Topuria", "lost_date": "2024-02-17"},
        
        # Bantamweight
        {"name": "Dominick Cruz", "weight_class": "Bantamweight", "lost_to": "Cody Garbrandt", "lost_date": "2016-12-30"},
        {"name": "Renan Barao", "weight_class": "Bantamweight", "lost_to": "T.J. Dillashaw", "lost_date": "2014-05-24"},
        {"name": "T.J. Dillashaw", "weight_class": "Bantamweight", "lost_to": "Dominick Cruz", "lost_date": "2016-01-17"},
        {"name": "Cody Garbrandt", "weight_class": "Bantamweight", "lost_to": "T.J. Dillashaw", "lost_date": "2017-11-04"},
        {"name": "Henry Cejudo", "weight_class": "Bantamweight", "lost_to": "Petr Yan", "lost_date": "2020-07-12"},
        {"name": "Petr Yan", "weight_class": "Bantamweight", "lost_to": "Aljamain Sterling", "lost_date": "2021-03-06"},
        {"name": "Aljamain Sterling", "weight_class": "Bantamweight", "lost_to": "Sean O'Malley", "lost_date": "2023-08-19"},
        {"name": "Sean O'Malley", "weight_class": "Bantamweight", "lost_to": "Merab Dvalishvili", "lost_date": "2024-09-14"},
        
        # Flyweight
        {"name": "Demetrious Johnson", "weight_class": "Flyweight", "lost_to": "Henry Cejudo", "lost_date": "2018-08-04"},
        {"name": "Deiveson Figueiredo", "weight_class": "Flyweight", "lost_to": "Brandon Moreno", "lost_date": "2021-06-12"},
        {"name": "Brandon Moreno", "weight_class": "Flyweight", "lost_to": "Deiveson Figueiredo", "lost_date": "2022-01-22"},
        {"name": "Brandon Moreno", "weight_class": "Flyweight", "lost_to": "Alexandre Pantoja", "lost_date": "2023-07-08"},
        
        # Women's Bantamweight
        {"name": "Ronda Rousey", "weight_class": "Women's Bantamweight", "lost_to": "Holly Holm", "lost_date": "2015-11-15"},
        {"name": "Holly Holm", "weight_class": "Women's Bantamweight", "lost_to": "Miesha Tate", "lost_date": "2016-03-05"},
        {"name": "Miesha Tate", "weight_class": "Women's Bantamweight", "lost_to": "Amanda Nunes", "lost_date": "2016-07-09"},
        {"name": "Amanda Nunes", "weight_class": "Women's Bantamweight", "lost_to": "Julianna Pena", "lost_date": "2021-12-11"},
        {"name": "Julianna Pena", "weight_class": "Women's Bantamweight", "lost_to": "Amanda Nunes", "lost_date": "2022-07-30"},
        {"name": "Raquel Pennington", "weight_class": "Women's Bantamweight", "lost_to": "Julianna Pena", "lost_date": "2024-10-05"},
        
        # Women's Flyweight
        {"name": "Valentina Shevchenko", "weight_class": "Women's Flyweight", "lost_to": "Alexa Grasso", "lost_date": "2023-03-04"},
        {"name": "Alexa Grasso", "weight_class": "Women's Flyweight", "lost_to": "Valentina Shevchenko", "lost_date": "2024-09-14"},
        
        # Women's Strawweight
        {"name": "Carla Esparza", "weight_class": "Women's Strawweight", "lost_to": "Joanna Jedrzejczyk", "lost_date": "2015-03-14"},
        {"name": "Joanna Jedrzejczyk", "weight_class": "Women's Strawweight", "lost_to": "Rose Namajunas", "lost_date": "2017-11-04"},
        {"name": "Rose Namajunas", "weight_class": "Women's Strawweight", "lost_to": "Jessica Andrade", "lost_date": "2019-05-11"},
        {"name": "Jessica Andrade", "weight_class": "Women's Strawweight", "lost_to": "Zhang Weili", "lost_date": "2019-08-31"},
        {"name": "Zhang Weili", "weight_class": "Women's Strawweight", "lost_to": "Rose Namajunas", "lost_date": "2021-04-24"},
        {"name": "Carla Esparza", "weight_class": "Women's Strawweight", "lost_to": "Zhang Weili", "lost_date": "2022-11-12"},
    ]
    
    return former_champions

def calculate_post_title_records(df, former_champions):
    """Calculate actual fight records after losing title."""
    results = []
    
    for champion in former_champions:
        name = champion['name']
        lost_date = pd.to_datetime(champion['lost_date'])
        
        # Find fights after losing title
        post_title_fights = df[
            (df['Date'] > lost_date) &
            ((df['RedFighter'] == name) | (df['BlueFighter'] == name))
        ]
        
        wins = losses = draws = 0
        
        for _, fight in post_title_fights.iterrows():
            if fight['RedFighter'] == name:
                if fight['Winner'] == 'Red':
                    wins += 1
                elif fight['Winner'] == 'Blue':
                    losses += 1
                else:
                    draws += 1
            elif fight['BlueFighter'] == name:
                if fight['Winner'] == 'Blue':
                    wins += 1
                elif fight['Winner'] == 'Red':
                    losses += 1
                else:
                    draws += 1
        
        total_fights = wins + losses + draws
        
        if total_fights > 0:  # Only include champions who fought after losing title
            win_percentage = round((wins / (wins + losses)) * 100, 1) if (wins + losses) > 0 else 0
            
            record_str = f"{wins}-{losses}"
            if draws > 0:
                record_str += f"-{draws}"
            
            results.append({
                "name": name,
                "record_after_belt": record_str,
                "title_loss_details": f"Lost {champion['weight_class']} title to {champion['lost_to']} on {champion['lost_date']}",
                "win_percentage": win_percentage,
                "weight_class": champion['weight_class'],
                "lost_to": champion['lost_to'],
                "wins_after_belt": wins,
                "losses_after_belt": losses,
                "draws_after_belt": draws,
                "total_fights_after_belt": total_fights
            })
    
    # Sort by win percentage descending
    results.sort(key=lambda x: x['win_percentage'], reverse=True)
    return results

def main():
    print("Processing complete UFC championship history...")
    
    # Load UFC data
    df = load_ufc_data()
    
    # Get former champions from history
    former_champions = get_former_champions_from_history()
    
    # Calculate their post-title records
    champions_with_records = calculate_post_title_records(df, former_champions)
    
    print(f"Found {len(champions_with_records)} former champions with post-title fights")
    
    # Save to file
    with open('complete_former_champions.json', 'w') as f:
        json.dump(champions_with_records, f, indent=2)
    
    print("Saved complete former champions list to 'complete_former_champions.json'")
    
    # Print summary
    print(f"\nTop 10 performers:")
    for i, champion in enumerate(champions_with_records[:10], 1):
        print(f"{i:2d}. {champion['name']:<25} {champion['record_after_belt']:<8} ({champion['win_percentage']:>5.1f}%) - {champion['weight_class']}")
    
    return champions_with_records

if __name__ == "__main__":
    main() 