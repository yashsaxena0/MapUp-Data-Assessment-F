import pandas as pd
import numpy as np 
from datetime import datetime, timedelta, time

def calculate_distance_matrix(df) ->pd.DataFrame():

    toll_locations = np.union1d(df['id_start'].unique(), df['id_end'].unique())
    distance_matrix = np.full((len(toll_locations), len(toll_locations)), np.inf)

# fill  with known distances
    for _, row in df.iterrows():
        start_idx = np.where(toll_locations == row['id_start'])[0][0]
        end_idx = np.where(toll_locations == row['id_end'])[0][0]
        distance_matrix[start_idx, end_idx] = row['distance']
        distance_matrix[end_idx, start_idx] = row['distance']
    np.fill_diagonal(distance_matrix, 0)

# compute cumulative distances using Floyd-Warshall algorithm
    for k in range(len(toll_locations)):
        for i in range(len(toll_locations)):
            for j in range(len(toll_locations)):
                if distance_matrix[i, j] > distance_matrix[i, k] + distance_matrix[k, j]:
                    distance_matrix[i, j] = distance_matrix[i, k] + distance_matrix[k, j]

    res_df = pd.DataFrame(distance_matrix, index=toll_locations, columns=toll_locations)
    return res_df

def unroll_distance_matrix(df) ->pd.DataFrame():
    locations = df.index.to_numpy()
    id_start_list = []
    id_end_list = []
    distance_list = []
    for start_idx, start_id in enumerate(locations):
        for end_idx, end_id in enumerate(locations):
            if start_idx != end_idx:
                distance = df.at[start_id, end_id]
                id_start_list.append(start_id)
                id_end_list.append(end_id)
                distance_list.append(distance)
    # Create a new DataFrame from the lists
    res_df = pd.DataFrame({'id_start': id_start_list, 'id_end': id_end_list, 'distance': distance_list})
    return res_df

def find_ids_within_ten_percentage_threshold(df,id_start) ->pd.DataFrame():
    calc_df=df[df['id_start']==id_start]
    avg=calc_df['distance'].mean()
    lower_threshold = avg - 0.1 * avg
    upper_threshold = avg + 0.1 * avg
    within_threshold = df[(df['distance'] >= lower_threshold) & (df['distance'] <= upper_threshold)]
    res_df=sorted(within_threshold['id_start'].unique())
    return res_df
    
def calculate_toll_rate(df) ->pd.DataFrame:
    rate = {'moto': 0.8, 'car': 1.2, 'rv': 1.5, 'bus': 2.2, 'truck': 3.6}
    res_df=pd.DataFrame(data=df)
    # Iterate over vehicle types and calculate toll rates
    for vehicle_type, rate_coeff in rate.items():
        res_df[vehicle_type] = df['distance'] * rate_coeff
    return res_df



def calculate_time_based_toll_rates(input_df) ->pd.DataFrame():
    # define time ranges and discount factors
    time_ranges = [
        (time(0, 0, 0), time(10, 0, 0), 0.8),
        (time(10, 0, 0), time(18, 0, 0), 1.2),
        (time(18, 0, 0), time(23, 59, 59), 0.8)
    ]
    
    weekend_discount_factor = 0.7
    result_rows = []
    # Iterate over unique (id_start, id_end) pairs
    for _, row in input_df.iterrows():
        start_datetime = datetime.combine(datetime.today(), time(0, 0, 0))
        end_datetime = datetime.combine(datetime.today(), time(23, 59, 59))

        for day in range(7):  # Loop through all days of the week
            for time_range in time_ranges:
                start_time, end_time, discount_factor = time_range
                start_datetime = start_datetime.replace(hour=start_time.hour, minute=start_time.minute, second=start_time.second)
                end_datetime = end_datetime.replace(hour=end_time.hour, minute=end_time.minute, second=end_time.second)

                # Apply discount factor based on weekday/weekend
                if day < 5:  # weekdays (Monday - Friday)
                    moto_rate = row['moto'] * discount_factor
                    car_rate = row['car'] * discount_factor
                    ev_rate = row['rv'] * discount_factor
                    bus_rate = row['bus'] * discount_factor
                    truck_rate = row['truck'] * discount_factor
                else:  # weekends (Saturday and Sunday)
                    moto_rate = row['moto'] * weekend_discount_factor
                    car_rate = row['car'] * weekend_discount_factor
                    ev_rate = row['rv'] * weekend_discount_factor
                    bus_rate = row['bus'] * weekend_discount_factor
                    truck_rate = row['truck'] * weekend_discount_factor

                result_rows.append({
                    'id_start': row['id_start'],
                    'id_end': row['id_end'],
                    'start_day': (datetime.today() + timedelta(days=day)).strftime('%A'),
                    'start_time': start_time,
                    'end_day': (datetime.today() + timedelta(days=day)).strftime('%A'),
                    'end_time': end_time,
                    'moto_rate': moto_rate,
                    'car_rate': car_rate,
                    'ev_rate': ev_rate,
                    'bus_rate': bus_rate,
                    'truck_rate': truck_rate
                })
    res_df = pd.DataFrame(result_rows)
    return res_df


