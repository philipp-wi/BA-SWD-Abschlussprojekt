import os
import sys
import json
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.append(os.path.abspath("modules")) # somehow mechanism cannot be found without this code line

from modules.json2config import load_mechanism_from_config
from modules.solver import NumericSolver
from modules.mechanism import Mechanism

# load available JSON configurations from "configurations" folder
def load_configurations():
    config_dir = "configurations"
    # create folder "configurations" if it does not exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return [f for f in os.listdir(config_dir) if f.endswith(".json")]

# generate animation with configuration from json2config
def generate_animation(mechanism, solver, frames=60, interval=100):
    rotation_center = None
    for joint in mechanism.joints:
        if joint.rotate_center is not None:
            rotation_center = joint.rotate_center
            break
    # plot settings
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(-50, 50)    # currently, the x and y limits are constant
    ax.set_ylim(-50, 50)    # however, they need to adjust for bigger mechanisms - still needs to be done
    ax.set_title("Animation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    
    # plot of the rotation center and rotation path in red color
    if rotation_center:
        ax.plot(rotation_center[0], rotation_center[1], 'ro', markersize=5)
        circle = plt.Circle(rotation_center, np.linalg.norm(np.array([joint.x, joint.y]) - np.array(rotation_center)), color='r', fill=False)
        ax.add_patch(circle)

    # plot rods as lines in blue color     
    rods_lines = [ax.plot([], [], 'bo-', lw=2)[0] for _ in mechanism.rods]
    
    # initialize animation with empty lines
    def init():
        for line in rods_lines:
            line.set_data([], [])
        return rods_lines
    
    # update animation for each frame
    def update_animation(frame):
        angle = np.deg2rad(frame * (360 / frames))
        solver.solve(angle)

        # update rod positions
        for line, rod in zip(rods_lines, mechanism.rods):
            x_data = [rod.start.x, rod.end.x]
            y_data = [rod.start.y, rod.end.y]
            line.set_data(x_data, y_data)
        return rods_lines
    
    # create animation as a gif
    animation_gif = animation.FuncAnimation(fig, update_animation, frames=frames, init_func=init, blit=True, interval=interval)
    gif_path = "animation.gif"
    animation_gif.save(gif_path, writer="pillow")
    return gif_path


def run_animation():
    st.title("Mechanism Animation")
    
    # load configurations
    config_files = load_configurations()
    if not config_files:
        st.warning("No configurations available! Please configurate a Mechanism or upload a configuration via configuration tab.")
        return
    
    selected_config = st.selectbox("Select a configuration", config_files)
    
    # start animation on button click
    if st.button("Start Animation"):
        config_path = os.path.join("configurations", selected_config)
        try:
            mechanism = load_mechanism_from_config(config_path)
            solver = NumericSolver(mechanism)
            gif_path = generate_animation(mechanism, solver)
            st.image(gif_path)
        # display error message    
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    run_animation()
