import pandas as pd
import numpy as numpy

def generate_car_matrix(df) -> pd.DataFrame:
    get_id_1=np.sort(df['id_1'].unique())
    get_id_2=np.sort(df['id_2'].unique())
    res_df=pd.DataFrame(index=get_id_1,columns=get_id_2)
    for i in get_id_1:
        for j in get_id_2:
            if i==j:
                continue
            res_df[i][j]=df[((df['id_1'] == i) & (df['id_2'] == j)) | ((df['id_1'] == j) & (df['id_2'] == i))]['car'].iloc[0]

    np.fill_diagonal(res_df.values,0.0)
    return res_df

def get_type_count(df) ->dict:
  def categorize_car(value):
    if value <= 15:
      return "low"
    elif 15 < value <= 25:
      return "medium"
    else:
      return "high"
  df["car_type"] = df["car"].apply(categorize_car)
  type_counts = df["car_type"].value_counts().to_dict()
  sorted_type_counts = dict(sorted(type_counts.items()))
  return sorted_type_counts

def get_bus_indexes(df)->list:
    mean=df['bus'].mean()
    return sorted(np.where(df['bus']>2*mean)[0])

def filter_routes(df)->list:
    avg_truck=df.groupby("route")["truck"].mean()
    routes = avg_truck[avg_truck > 7]
    sorted_routes = routes.index.to_list()
    sorted_routes.sort()
    return sorted_routes

def multiply_matrix(df) -> pd.DataFrame:
    def conditional_multiply(value):
        if value > 20:
            return value * 0.75
        else:
            return value * 1.25
    res_df=df.applymap(conditional_multiply)
    res_df_rounded=res_df.round(1)
    return res_df_rounded


def time_check(df) ->pd.Series:
    # Convert timestamp columns to datetime format
    df['start_datetime'] = pd.to_datetime(df['startDay'] + ' ' + df['startTime'], format='%A %H:%M:%S')
    df['end_datetime'] = pd.to_datetime(df['endDay'] + ' ' + df['endTime'], format='%A %H:%M:%S')
    full_24_hours = pd.date_range('00:00:00', '23:59:59', freq='1S')        #Create full 24-hour period timestamp
    completeness_check = pd.DataFrame(index=df.set_index(['id', 'id_2']).index)

    # Check completeness for each unique (id, id_2) pair
    for (id_value, id_2_value), group_df in df.groupby(['id', 'id_2']):
        start_datetime = group_df['start_datetime'].min()
        end_datetime = group_df['end_datetime'].max()

        # Check if timestamps cover a full 24-hour period
        full_24_hours_coverage = (
            (start_datetime <= full_24_hours).min() and
            (end_datetime >= full_24_hours).max()
        )

       
        days_of_week_span = set(group_df['start_datetime'].dt.dayofweek.unique()) == set(range(7))  # Check if timestamps span all 7 days of the week

        completeness_check.loc[(id_value, id_2_value), 'completeness'] = full_24_hours_coverage and days_of_week_span.all()
    return completeness_check['completeness']

