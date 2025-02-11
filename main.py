import streamlit as st
import pandas as pd
import json

st.title("Mechanism Simulator")

st.write("**This application allows you to simulate mechanical mechanism**")
st.markdown(""" - In the configuration tab you can define joints and rods to create a custom mechanism. Strandbeest and Viergelenkkette configurations are already available.""")
st.markdown("""
- In the animation tab you can select a configuration and simulate the mechanism.
  - Animation of Mechanism (GIF)
  - Generate frame of mechanism at specific degree (PNG)
  - Save joint coordinates (CSV)          
""")

st.title("Leaderboard:")
st.write("Here you can see the times of the PC's trying to simulate various configurations. Rendering times will only be ranked if you use default settings (simulation resolution = 10.00 and framerate = 60.00).")

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