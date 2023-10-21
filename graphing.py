import plotly.express as px
import pandas as pd


data = pd.read_csv('test_results/250_sim_users_gin/250_sim_users_stats_history.csv')
# data_no_duplicates = data.drop_duplicates(subset=['Timestamp'])
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='s')

# Calculate the time elapsed from the first timestamp
data['TimeElapsed'] = (data['Timestamp'] - data['Timestamp'].iloc[0]).dt.total_seconds()

# Convert the time elapsed to minutes and seconds
data['TimeElapsed'] = data['TimeElapsed'].apply(lambda x: f"{int(x/60):02d}:{int(x%60):02d}")

# Subtract the minimum timestamp from all timestamps to make the first timestamp start at 0
fig = px.line(data, x="TimeElapsed", y="Requests/s", title='Gin 500 Users Get Adventure Stress Test')
fig.update_xaxes(range=[0, 20 * 60])
fig.show()