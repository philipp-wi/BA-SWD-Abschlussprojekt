import streamlit as st
import pandas as pd
import json

st.title("Mechanism Simulator")

st.write("Here you can simulate a mechanism by defining its configuration and then running the simulation.")

st.title("Leaderboard:")
st.write("Here you can see the times of the PC's trying to simulate various configurations.")

# Load leaderboard data from JSON file
with open('leaderboard.json', 'r') as file:
    leaderboard_data = json.load(file)

# Convert JSON data to DataFrame
data = {'Configuration': [], 'PC': [], 'Time': []}
for config, pcs in leaderboard_data.items():
    for pc, time in pcs.items():
        data['Configuration'].append(config)
        data['PC'].append(pc)
        data['Time'].append(time)

df = pd.DataFrame(data)


selected_config = st.selectbox("Select Configuration", df['Configuration'].unique())

filtered_df = df[df['Configuration'] == selected_config].drop(columns=['Configuration']).set_index('PC')
filtered_df = filtered_df.sort_values(by='Time')
filtered_df['Rank'] = range(1, len(filtered_df) + 1)
filtered_df = filtered_df.reset_index()
filtered_df = filtered_df[['Rank', 'PC', 'Time']]

st.table(filtered_df.set_index('Rank'))