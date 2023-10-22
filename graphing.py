import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from plotly.offline import plot
import pandas as pd


gin_data = pd.read_csv('test_results/rails_gin_250_sim_users_10min/gin_250_sim_users.csv_stats.csv')
rails_data = pd.read_csv('test_results/rails_gin_250_sim_users_10min/rails_250_sim_users.csv_stats.csv')
rails_aggregate = rails_data['Name'] == 'Aggregated'
gin_aggregate = gin_data['Name'] == 'Aggregated'
rails_data = rails_data[rails_data['Name'] != 'Aggregated']
gin_data = gin_data[gin_data['Name'] != 'Aggregated']

gin_values = gin_data["Request Count"].tolist()
gin_labels = gin_data["Name"].tolist()
gin_total_requests = gin_aggregate
rails_total_requests = rails_aggregate

rails_values = rails_data["Request Count"].tolist()
rails_labels = rails_data["Name"].tolist()

fig = make_subplots(rows=1, cols=2, specs=[[{"type": "pie"}, {"type": "pie"}]])


fig.add_trace(go.Pie(
    values=gin_values,
    labels=gin_labels,
    title="Gin User Sim Requests. Total Requests: 38208"
), row=1, col=1)

fig.add_trace(go.Pie(
    values=rails_values,
    labels=rails_labels,
    title="Rails User Sim Requests. Total Requests: 27282"
),row=1, col=2)

fig.show()