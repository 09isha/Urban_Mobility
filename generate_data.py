import pandas as pd
import numpy as np
import sqlite3
import datetime
import random
import os

np.random.seed(42)
random.seed(42)

# Constants
NUM_RIDES = 75000
NUM_RIDERS = 15000
NUM_DRIVERS = 3000

CITIES = ['Metroville', 'Capital City']
ZONES = {
    'Metroville': ['Downtown', 'Airport', 'Residential North', 'Tech Park', 'Suburbs'],
    'Capital City': ['Central Business District', 'University Area', 'Industrial Zone', 'Westside']
}

# Zone Demand Multipliers
ZONE_DEMAND = {
    'Downtown': 2.5, 'Airport': 1.8, 'Residential North': 1.2, 'Tech Park': 2.0, 'Suburbs': 0.8,
    'Central Business District': 2.2, 'University Area': 1.5, 'Industrial Zone': 0.9, 'Westside': 1.1
}

START_DATE = datetime.datetime(2023, 1, 1)
END_DATE = datetime.datetime(2023, 3, 31)
DATE_RANGE_DAYS = (END_DATE - START_DATE).days

def generate_riders():
    print("Generating Riders...")
    riders = []
    for i in range(1, NUM_RIDERS + 1):
        city = np.random.choice(CITIES, p=[0.6, 0.4])
        signup_offset = random.randint(0, 365*2)
        signup_date = START_DATE - datetime.timedelta(days=signup_offset)
        rider_type = np.random.choice(['Regular', 'Occasional', 'New', 'Power'], p=[0.4, 0.3, 0.1, 0.2])
        riders.append([f'R{i:06d}', city, signup_date.strftime('%Y-%m-%d'), rider_type])
    
    return pd.DataFrame(riders, columns=['rider_id', 'city', 'signup_date', 'rider_type'])

def generate_drivers():
    print("Generating Drivers...")
    drivers = []
    for i in range(1, NUM_DRIVERS + 1):
        city = np.random.choice(CITIES, p=[0.6, 0.4])
        join_offset = random.randint(0, 365*3)
        join_date = START_DATE - datetime.timedelta(days=join_offset)
        experience_months = join_offset // 30
        vehicle_type = np.random.choice(['Standard', 'Premium', 'XL', 'Electric'], p=[0.6, 0.15, 0.15, 0.1])
        drivers.append([f'D{i:05d}', city, join_date.strftime('%Y-%m-%d'), experience_months, vehicle_type])
    
    return pd.DataFrame(drivers, columns=['driver_id', 'city', 'join_date', 'experience_months', 'vehicle_type'])

def generate_rides(riders_df, drivers_df):
    print("Generating Rides...")
    
    # Pre-calculate driver availability pools by city
    drivers_by_city = {city: drivers_df[drivers_df['city'] == city]['driver_id'].tolist() for city in CITIES}
    riders_by_city = {city: riders_df[riders_df['city'] == city]['rider_id'].tolist() for city in CITIES}
    
    rides = []
    
    for i in range(1, NUM_RIDES + 1):
        city = np.random.choice(CITIES, p=[0.6, 0.4])
        zone = np.random.choice(ZONES[city])
        
        # Generate datetime with peaks
        day_offset = random.randint(0, DATE_RANGE_DAYS)
        is_weekend = (START_DATE + datetime.timedelta(days=day_offset)).weekday() >= 5
        
        # Hourly distribution
        if is_weekend:
            # Flatter distribution on weekends, slight evening peak
            hour_probs = [1]*7 + [2]*3 + [3]*4 + [4]*4 + [5]*4 + [3]*2
        else:
            # Morning peak (7-9), Evening peak (17-19)
            hour_probs = [1]*6 + [3, 8, 9, 5] + [3]*6 + [4, 8, 9, 6] + [3, 2, 1, 1]
        
        hour_probs = np.array(hour_probs) / sum(hour_probs)
        hour = np.random.choice(24, p=hour_probs)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        request_time = START_DATE + datetime.timedelta(days=day_offset, hours=int(hour), minutes=minute, seconds=second)
        
        # Demand-supply logic
        base_demand = hour_probs[hour] * 100 * ZONE_DEMAND[zone]
        
        # Simulate supply shortage in certain conditions (e.g. Airport on Monday mornings, Tech Park on weekday evenings)
        supply_shortage = False
        if not is_weekend and ((hour in [8,9] and zone == 'Downtown') or (hour in [17,18,19] and zone == 'Tech Park')):
            supply_shortage = True
            
        surge_multiplier = 1.0
        if supply_shortage:
            surge_multiplier = round(random.uniform(1.5, 3.0), 1)
        elif base_demand > 5:
            surge_multiplier = round(random.uniform(1.1, 1.5), 1)
            
        # Determine Status
        cancel_prob = 0.05
        if surge_multiplier > 2.0: cancel_prob += 0.15
        if supply_shortage: cancel_prob += 0.20
        
        status = np.random.choice(['Completed', 'Cancelled_Rider', 'Cancelled_Driver'], p=[1-cancel_prob, cancel_prob*0.7, cancel_prob*0.3])
        
        rider_id = random.choice(riders_by_city[city])
        driver_id = random.choice(drivers_by_city[city]) if status != 'Cancelled_Rider' else None
        
        wait_time = None
        trip_duration = None
        distance_km = None
        fare = None
        pickup_time = None
        completion_time = None
        cancellation_reason = None
        
        if status == 'Completed':
            # Wait time based on supply
            base_wait = random.uniform(2, 8)
            if supply_shortage: base_wait += random.uniform(5, 15)
            wait_time = round(base_wait, 1)
            
            pickup_time = request_time + datetime.timedelta(minutes=wait_time)
            
            # Trip stats
            distance_km = round(random.uniform(1, 25), 1)
            speed_kmh = random.uniform(20, 45)
            if hour in [8, 9, 17, 18]: speed_kmh *= 0.7 # Traffic
            trip_duration = round((distance_km / speed_kmh) * 60, 1)
            
            completion_time = pickup_time + datetime.timedelta(minutes=trip_duration)
            
            # Fare calculation
            base_fare = 2.5
            per_km = 1.2
            per_min = 0.15
            fare = round((base_fare + (distance_km * per_km) + (trip_duration * per_min)) * surge_multiplier, 2)
            
        elif status == 'Cancelled_Rider':
            wait_time = round(random.uniform(0.5, 5), 1) # Time before they cancelled
            if surge_multiplier > 1.5:
                cancellation_reason = 'Price too high'
            else:
                cancellation_reason = 'Wait time too long'
        else: # Cancelled_Driver
            wait_time = round(random.uniform(2, 10), 1)
            cancellation_reason = 'Rider no-show' if random.random() > 0.5 else 'Vehicle issue'
            
        rides.append([
            f'REQ{i:07d}', rider_id, driver_id, city, zone, 
            request_time.strftime('%Y-%m-%d %H:%M:%S'), 
            pickup_time.strftime('%Y-%m-%d %H:%M:%S') if pickup_time else None, 
            completion_time.strftime('%Y-%m-%d %H:%M:%S') if completion_time else None, 
            distance_km, fare, surge_multiplier, wait_time, trip_duration, status, cancellation_reason
        ])
        
    df = pd.DataFrame(rides, columns=[
        'ride_id', 'rider_id', 'driver_id', 'city', 'zone', 
        'request_time', 'pickup_time', 'completion_time', 
        'distance_km', 'fare', 'surge_multiplier', 'wait_time', 
        'trip_duration', 'status', 'cancellation_reason'
    ])
    
    return df

def main():
    print("Starting data generation...")
    riders_df = generate_riders()
    drivers_df = generate_drivers()
    rides_df = generate_rides(riders_df, drivers_df)
    
    # Save to CSV
    print("Saving to CSV...")
    riders_df.to_csv('riders.csv', index=False)
    drivers_df.to_csv('drivers.csv', index=False)
    rides_df.to_csv('rides.csv', index=False)
    
    # Save to SQLite
    print("Saving to SQLite database (move.db)...")
    conn = sqlite3.connect('move.db')
    riders_df.to_sql('riders', conn, if_exists='replace', index=False)
    drivers_df.to_sql('drivers', conn, if_exists='replace', index=False)
    rides_df.to_sql('rides', conn, if_exists='replace', index=False)
    conn.close()
    
    print("Data generation complete!")

if __name__ == "__main__":
    main()
