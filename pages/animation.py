import os
import sys
import csv
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.animation as animation

sys.path.append(os.path.abspath("modules")) # somehow mechanism cannot be found without this code line

from modules.json2config import load_mechanism_from_config
from modules.solver import NumericSolver

# load available JSON configurations from "configurations" folder
def load_configurations():
    config_dir = "configurations"
    # create folder "configurations" if it does not exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    return [f for f in os.listdir(config_dir) if f.endswith(".json")]

def get_joint_coords(mechanism):
    return [(joint.x, joint.y) for joint in mechanism.joints]

def calculate_solved_coords(mechanism, solver, start_deg, end_deg, num_frames): # returns dictionary of frame index to joint position
    angles = np.linspace(start_deg, end_deg, num_frames)
    solved = {}
    for i, angle in enumerate(angles):
        solver.solve(np.deg2rad(angle))
        solved[i] = get_joint_coords(mechanism)
    return solved, angles

def save_moving_coords_csv(solved_coords, angles): # saves moving coordinates to a CSV file
    csv_path = "moving_coords.csv"
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["joint_nr", "angle", "x_pos", "y_pos"])
        for frame in sorted(solved_coords.keys()):
            angle = angles[frame]
            joints = solved_coords[frame]
            for joint_nr, (x, y) in enumerate(joints):
                writer.writerow([joint_nr, angle, x, y])
    return csv_path

def get_axis_limits(solved_coords): # reads in solved coordinates and returns axis limits rounded to the next multiple of 5
    all_x, all_y = [], []           # (might be making erros at specific configurations when the fixed joint is further away than the moving joint -> test?)
    for coords in solved_coords.values():
        for (x, y) in coords:
            all_x.append(x)
            all_y.append(y)
    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    x_lim = (int(x_min // 5 * 5), int((x_max // 5 + 1) * 5))
    y_lim = (int(y_min // 5 * 5), int((y_max // 5 + 1) * 5))
    return x_lim, y_lim

def draw_frame(mechanism, coords, x_lim, y_lim): # draws a single frame of the mechanism at the given joint coordinates
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_title("Mechanism Frame")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    
    # Plot rotation center
    rotation_center = None
    for joint in mechanism.joints:
        if joint.rotate_center is not None:
            rotation_center = joint.rotate_center
            break
    if rotation_center:
        ax.plot(rotation_center[0], rotation_center[1], 'ro', markersize=5)
        circle = plt.Circle(rotation_center, np.linalg.norm(np.array([joint.x, joint.y]) - np.array(rotation_center)), color='r', fill=False)
        ax.add_patch(circle)
    
    # Plot rods as blue lines.
    for rod in mechanism.rods:
        s_idx = mechanism.joints.index(rod.start)
        e_idx = mechanism.joints.index(rod.end)
        sx, sy = coords[s_idx]
        ex, ey = coords[e_idx]
        ax.plot([sx, ex], [sy, ey], 'bo-', lw=2)

    # Plot joints as green dots. (deactivated to match animation)
    #for (x, y) in coords:
    #    ax.plot(x, y, 'go')
    
    img_path = "frame.png"
    fig.savefig(img_path)
    plt.close(fig)
    return img_path

def generate_animation(mechanism, solved_coords, interval): # generates an animation of the mechanism
    frames = len(solved_coords)
    x_lim, y_lim = get_axis_limits(solved_coords)
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(x_lim)
    ax.set_ylim(y_lim)
    ax.set_title(f"Mechanism Animation")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    
    # Plot rotation center
    rotation_center = None
    for joint in mechanism.joints:
        if joint.rotate_center is not None:
            rotation_center = joint.rotate_center
            break
    if rotation_center:
        ax.plot(rotation_center[0], rotation_center[1], 'ro', markersize=5)
        circle = plt.Circle(rotation_center, np.linalg.norm(np.array([joint.x, joint.y]) - np.array(rotation_center)), color='r', fill=False)
        ax.add_patch(circle)
    
    # Create a line for each rod.
    rods_lines = [ax.plot([], [], 'bo-', lw=2)[0] for _ in mechanism.rods]
    
    def initialize_lines():
        for line in rods_lines:
            line.set_data([], [])
        return rods_lines
    
    def update(frame):
        coords = solved_coords[frame]
        for line, rod in zip(rods_lines, mechanism.rods):
            s_idx = mechanism.joints.index(rod.start)
            e_idx = mechanism.joints.index(rod.end)
            sx, sy = coords[s_idx]
            ex, ey = coords[e_idx]
            line.set_data([sx, ex], [sy, ey])
        return rods_lines
    
    ani = animation.FuncAnimation(fig, update, frames=frames, init_func=initialize_lines,
                                  blit=True, interval=interval)
    gif_path = "animation.gif"
    ani.save(gif_path, writer="pillow")
    plt.close(fig)
    return gif_path

def grafic_engine():
    st.title("Mechanism Visualization")
    
    # Load configuration files.
    config_files = load_configurations()
    if not config_files:
        st.warning("No configuration files found in the 'configurations' folder!")
        return
    selected_config = st.selectbox("Select a configuration", config_files)
    config_path = os.path.join("configurations", selected_config)
    
    # Initialize mechanism and solver.
    try:
        mechanism = load_mechanism_from_config(config_path)
        solver = NumericSolver(mechanism)
    except Exception as e:
        st.error(f"Error loading configuration: {e}")
        return

    # Simulation parameters.
    st.markdown("### Simulation Parameters")
    sim_resolution = st.number_input("Simulation resolution (degrees per step):", min_value=0.1, value=1.0, step=0.1)
    framerate = st.number_input("Framerate (frames per second):", min_value=1, value=60, step=1)
    interval = 1000 / framerate

    # Button to download moving coordinates as CSV.
    if st.button("Generate Moving Coordinates CSV"):
        # Compute moving coordinates for a full cycle (0° to 360°)
        num_frames = int((360 - 0) / sim_resolution) + 1
        solved_coords, angles = calculate_solved_coords(mechanism, solver, 0, 360, num_frames)
        csv_path = save_moving_coords_csv(solved_coords, angles)
        with open(csv_path, "rb") as file:
            st.download_button(label="Download CSV",
                               data=file,
                               file_name="moving_coords.csv",
                               mime="text/csv")

    # Render single frame.
    st.markdown("### Render a Single Frame")
    frame_angle_str = st.text_input("Frame angle (degrees):", "0")
    if st.button("Render Frame"):
        try:
            frame_angle = float(frame_angle_str)
        except ValueError:
            st.error("Invalid frame angle")
            return
        # Precompute full cycle positions (0° to 360° in 361 frames) to set axis limits.
        full_coords, _ = calculate_solved_coords(mechanism, solver, 0, 360, 361) # unfortunatly very inefficient for only one frame
        #full_coords, _ = compute_solved_coords(mechanism, solver, 0, frame_angle, 1) # to set axis limits only for the current frame (mostyl to nerrow)
        x_lim, y_lim = get_axis_limits(full_coords)

        # Solve for the requested frame.
        solver.solve(np.deg2rad(frame_angle))
        curr_coords = get_joint_coords(mechanism)
        img_path = draw_frame(mechanism, curr_coords, x_lim, y_lim)
        st.image(img_path, caption=f"Frame at {frame_angle}°")
        with open(img_path, "rb") as file:
            st.download_button(label="Download Frame",
                               data=file,
                               file_name=f"mechanism_frame_angle_{frame_angle}.png",
                               mime="image/png")
    
    # Render animation.
    st.markdown("### Render Animation")
    start_angle_str = st.text_input("Start angle (°):", "0", key="anim_start")
    end_angle_str   = st.text_input("End angle (°):", "360", key="anim_end")
    if st.button("Render Animation"):
        try:
            start_angle = float(start_angle_str)
            end_angle   = float(end_angle_str)
        except ValueError:
            st.error("Invalid start or end angle")
            return
        num_frames = int((end_angle - start_angle) / sim_resolution)

        solved_coords, angle = calculate_solved_coords(mechanism, solver, start_angle, end_angle, num_frames)
        x_lim, y_lim = get_axis_limits(solved_coords)
        gif_path = generate_animation(mechanism, solved_coords, interval)
        st.image(gif_path, caption="Mechanism Animation")
        with open(gif_path, "rb") as file:
            st.download_button(label="Download Animation",
                               data=file,
                               file_name="mechanism_animation.gif",
                               mime="image/gif")

if __name__ == "__main__":
    grafic_engine()
