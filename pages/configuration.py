import streamlit as st
import pandas as pd
import json
import os

def mechanism_configuration():
    st.title("Mechanism Configuration")
    
    config_name = st.text_input("Configuration Name", placeholder="Enter configuration name")
    st.write("## Define Joints")
    
    # joint table
    if "joints" not in st.session_state:
        st.session_state.joints = pd.DataFrame(
            # joint_name, x-coords, y-coords, select pinned/static joint, select rotating joint 
            columns=["joint_name", "x", "y", "pinned", "rotating_joint"],
            data=[
                ["p0", 0.0, 0.0, True, False], 
                ["p1", 10.0, 35.0, False, False], 
                ["p2", -25.0, 10.0, False, True],
                ["p3", -30.0, 0.0, True, False]     # keep example values in the initial table, otherwise the table might bug
            ]
        )

    # data editor for modifying joints
    edited_joints = st.data_editor(
        st.session_state.joints,
        num_rows="dynamic",
        key="joints_editor"
    )

    # check if only one rotating joint checked
    joint_error = False
    if edited_joints["rotating_joint"].sum() < 1:
        joint_error = True
        st.error("At least one joint must be a rotating joint!")
    else:
        joint_error = False
    
    # dropdown to select rotation center from already defined joints
    joint_names = edited_joints["joint_name"].tolist()
    rotation_center = st.selectbox("Select Rotation Center", joint_names if joint_names else ["None"])
    
    st.write("## Define Rods")
    st.write("Connect two joints to create a rod")

    # rods table
    if "rods" not in st.session_state:
        st.session_state.rods = pd.DataFrame(
            columns=["start_joint", "end_joint"],
            data=[[joint_names[0], joint_names[1]] if len(joint_names) > 1 else ["", ""]]
        )
    
    # data editor for modifying rods
    edited_rods = st.data_editor(
        st.session_state.rods,
        num_rows="dynamic",
        key="rods_editor"
    )

    # check if any rod has the same start and end joint
    rods_error = False
    for _, row in edited_rods.iterrows():
        if row["start_joint"] == row["end_joint"]:
            rods_error = True
            st.error(f"Rod cannot have the same start and end joint: {row['start_joint']}")
        else:
            rods_error = False

    
    # function to export the configuration as a JSON file
    def export_to_json():
        if not config_name.strip():
            st.error("Enter a configuration name!")
            return
        
        # list of joints with properties
        joints_list = []
        for _, row in edited_joints.iterrows():
            joints_list.append({
                "joint_name": row["joint_name"],
                "x": row["x"],
                "y": row["y"],
                "pinned": bool(row["pinned"]),
                "rotating_joint": bool(row["rotating_joint"])
            })
        
        # list of rods with start and end joints
        rods_list = []
        for _, row in edited_rods.iterrows():
            rods_list.append({
                "start_joint": row["start_joint"],
                "end_joint": row["end_joint"]
            })
        
        # create output for JSON file
        output_data = {
            "configuration_name": config_name,
            "joints": joints_list,
            "rotation_center": rotation_center,
            "rods": rods_list
        }
        
        # create "configurations" folder if it doesn't exist already
        os.makedirs("configurations", exist_ok=True)
        filename = os.path.join("Configurations", f"{config_name.replace(' ', '_')}_configuration.json")
        
        # save data as JSON file
        with open(filename, "w") as f:
            json.dump(output_data, f, indent=4)
        st.success(f"Configuration saved!")
    
    # export button to save the configuration
    if st.button("Export to JSON"):
        if joint_error or rods_error:
            st.error("Fix the errors before exporting!")
        else:
            export_to_json()
    
    st.markdown("---")
    
    # configuration upload field
    uploaded_file = st.file_uploader("Upload a configuration file (JSON)", type=["json"]) # only allow JSON files
    if uploaded_file is not None:
        try:
            os.makedirs("configurations", exist_ok=True)
            file_path = os.path.join("configurations", uploaded_file.name)
            
            # save the upload file in the "configurations" folder
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Configuration uploaded successfully!")
        except Exception as e:
            st.error(f"Error!")
    
if __name__ == "__main__":
    mechanism_configuration()
