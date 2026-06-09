import pandas as pd
import numpy as np
from faker import Faker
import datetime
import random
import os
import config

fake = Faker()

def generate_users(num_users):
    print(f"Generating {num_users} users...")
    segments = ['New Users', 'Retail Traders', 'Power Users', 'Whales', 'Inactive Users']
    devices = ['iOS', 'Android', 'Web']
    
    users = []
    for user_id in range(1, num_users + 1):
        users.append({
            'user_id': user_id,
            'country': fake.country_code(),
            'segment': np.random.choice(segments, p=[0.2, 0.4, 0.2, 0.05, 0.15]),
            'device': np.random.choice(devices, p=[0.4, 0.4, 0.2]),
            'join_date': fake.date_time_between(start_date=config.START_DATE, end_date=config.END_DATE)
        })
    return pd.DataFrame(users)

def generate_events(users_df, num_events):
    print(f"Generating {num_events} events...")
    
    # Pre-calculate base event weights based on user segment
    segment_activity_multiplier = {
        'New Users': 1,
        'Retail Traders': 5,
        'Power Users': 20,
        'Whales': 50,
        'Inactive Users': 0.1
    }
    
    user_ids = users_df['user_id'].values
    user_segments = users_df['segment'].values
    
    # Create a mapping of user_id to activity multiplier
    activity_weights = np.array([segment_activity_multiplier[seg] for seg in user_segments])
    activity_probs = activity_weights / activity_weights.sum()

    # The funnel stages
    # Search -> View Page -> View Orderbook -> Trade
    # Conversion rates drop off at each step
    
    events = []
    
    # Time settings
    start_ts = pd.to_datetime(config.START_DATE).timestamp()
    end_ts = pd.to_datetime(config.END_DATE).timestamp()
    
    # Trending factors
    # Let's say PEPE searches spiked heavily later in the period
    
    batch_size = 10000
    for i in range(0, num_events, batch_size):
        if i % 100000 == 0:
            print(f"{i}/{num_events} events generated")
            
        current_batch_size = min(batch_size, num_events - i)
        
        # Pick users for this batch based on activity probability
        batch_users = np.random.choice(user_ids, size=current_batch_size, p=activity_probs)
        
        # Pick timestamps
        batch_ts = np.random.uniform(start_ts, end_ts, current_batch_size)
        
        # Pick base tokens (some more popular)
        token_probs = [0.3, 0.2, 0.15, 0.1, 0.05, 0.05, 0.05, 0.05, 0.03, 0.02]
        batch_tokens = np.random.choice(config.TOKENS, size=current_batch_size, p=token_probs)
        
        for j in range(current_batch_size):
            u_id = batch_users[j]
            ts = batch_ts[j]
            token = batch_tokens[j]
            dt = datetime.datetime.fromtimestamp(ts)
            
            # Artificial trend: PEPE spikes in April/May
            if dt.month in [4, 5] and random.random() < 0.3:
                token = 'PEPE'
                
            # Simulate a funnel session for this user/token/time
            
            # 1. Always start with search (for this dataset's context) or just direct token page
            events.append({'user_id': u_id, 'event_type': 'search', 'token': token, 'timestamp': dt})
            
            # 2. View token page (75% conversion from search)
            if random.random() < 0.75:
                dt += datetime.timedelta(seconds=random.randint(5, 30))
                events.append({'user_id': u_id, 'event_type': 'view_token_page', 'token': token, 'timestamp': dt})
                
                # Watchlist action (10% of page views)
                if random.random() < 0.10:
                    events.append({'user_id': u_id, 'event_type': 'add_to_watchlist', 'token': token, 'timestamp': dt + datetime.timedelta(seconds=2)})
                
                # 3. View Orderbook (56% conversion from token page view) -> 42% overall
                if random.random() < 0.56:
                    dt += datetime.timedelta(seconds=random.randint(10, 60))
                    events.append({'user_id': u_id, 'event_type': 'view_orderbook', 'token': token, 'timestamp': dt})
                    
                    # 4. Trade Execution (47% from orderbook) -> ~20% overall
                    if random.random() < 0.47:
                        dt += datetime.timedelta(seconds=random.randint(10, 120))
                        events.append({'user_id': u_id, 'event_type': 'trade_executed', 'token': token, 'timestamp': dt})
                        
    # Because we added multiple events per iteration, we might overshoot num_events, 
    # but that's fine, we will just return a realistic funnel dataset
    return pd.DataFrame(events)

if __name__ == "__main__":
    np.random.seed(42)
    random.seed(42)
    Faker.seed(42)
    
    print("Starting data generation...")
    users_df = generate_users(config.NUM_USERS)
    users_df.to_csv("users.csv", index=False)
    print("Saved users.csv")
    
    # Note: to get ~500k total events, we might need fewer base loops because of the funnel multiplying events
    # Let's say ~2.5 events per loop on average. So 200k base loops -> 500k events.
    base_loops = config.NUM_EVENTS // 2
    events_df = generate_events(users_df, base_loops)
    events_df.to_csv("events.csv", index=False)
    print(f"Saved events.csv with {len(events_df)} rows")
    print("Data generation complete!")
