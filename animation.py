import streamlit as st
import json
import os
import matplotlib.pyplot as plt

# load available configurations from "configurations" folder
def load_configurations():
    config_dir = "configurations"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    return [f for f in os.listdir(config_dir) if f.endswith(".json")]

def run_animation():
    st.title("Mechanism Animation")
    
    config_files = load_configurations()
    if not config_files:
        st.warning("No configurations available!")
        return
    
    st.selectbox("Select a configuration", config_files)
    
    if st.button("Start Animation"): # button has no action yet
        pass
    
if __name__ == "__main__":
    run_animation()