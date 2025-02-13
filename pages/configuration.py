import streamlit as st
import pandas as pd
import json
import os

def mechanism_configuration():
    st.title("Mechanism Configuration")
    
    # load existing configurations from folder
    config_folder = "configurations"
    os.makedirs(config_folder, exist_ok=True)
    config_files = ["New Configuration"] + [f for f in os.listdir(config_folder) if f.endswith(".json")]
    selected_config = st.selectbox("Select Configuration", config_files)  # Auswahl Dropdown
    
    # configuration name input field
    config_name = "" if selected_config == "New Configuration" else selected_config.replace("_configuration.json", "")
    config_name = st.text_input("Configuration Name", value=config_name, placeholder="Enter configuration name")
    
    # load data
    loaded_joints = []
    loaded_rods = []
    rotation_center = "None"
    
    if selected_config != "New Configuration":
        file_path = os.path.join(config_folder, selected_config)
        try:
            with open(file_path, "r") as f:
                config_data = json.load(f)
                loaded_joints = config_data.get("joints", [])
                loaded_rods = config_data.get("rods", [])
                rotation_center = config_data.get("rotation_center", "None")
        except Exception as e:
            st.error("Error loading configuration file!")
    
    st.write("## Define Joints")
    
    # joint table
    if "joints" not in st.session_state or selected_config != "New Configuration":
        st.session_state.joints = pd.DataFrame(loaded_joints if loaded_joints else [
            {"joint_name": "p0", "x": 0.0, "y": 0.0, "pinned": True, "rotating_joint": False},
            {"joint_name": "p1", "x": 10.0, "y": 0.0, "pinned": False, "rotating_joint": True}
        ])
    
    # data editor for modifying joints
    edited_joints = st.data_editor(
        st.session_state.joints,
        num_rows="dynamic",
        key="joints_editor"
    )
    
    # check if only one rotating joint checked
    joint_names = edited_joints["joint_name"].tolist()
    joint_error = False
    if edited_joints["rotating_joint"].sum() < 1:
        joint_error = True
        st.error("At least one joint must be a rotating joint!")
    
    # dropdown to select rotation center from already defined joints
    rotation_center = st.selectbox("Select Rotation Center", joint_names if joint_names else ["None"], index=joint_names.index(rotation_center) if rotation_center in joint_names else 0)
    
    st.write("## Define Rods")
    st.write("Connect two joints to create a rod")  # Wieder eingefügter Kommentar
    
    # rods table
    if "rods" not in st.session_state or selected_config != "New Configuration":
        st.session_state.rods = pd.DataFrame(loaded_rods if loaded_rods else [
            {"start_joint": joint_names[0], "end_joint": joint_names[1]} if len(joint_names) > 1 else {"start_joint": "", "end_joint": ""}
        ])
    
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
    
    # function to export the configuration as a JSON file
    def export_to_json():
        if not config_name.strip():
            st.error("Enter a configuration name!")
            return
        
        # list of joints with properties
        joints_list = edited_joints.to_dict(orient="records")
        # list of rods with start and end joints
        rods_list = edited_rods.to_dict(orient="records")
        
        # create output for JSON file
        output_data = {
            "configuration_name": config_name,
            "joints": joints_list,
            "rotation_center": rotation_center,
            "rods": rods_list
        }
        
        # create "configurations" folder if it doesn't exist already
        filename = os.path.join(config_folder, f"{config_name.replace(' ', '_')}_configuration.json")
        
        # save data as JSON file
        with open(filename, "w") as f:
            json.dump(output_data, f, indent=4)
        st.success(f"Configuration saved!")
    
    # export button to save the configuration
    if st.button("Save configuration"):
        if joint_error or rods_error:
            st.error("Fix the errors before exporting!")
        else:
            export_to_json()

    # download configuration as JSON
    if config_name.strip():
        output_data = {
            "configuration_name": config_name,
            "joints": edited_joints.to_dict(orient="records"),
            "rotation_center": rotation_center,
            "rods": edited_rods.to_dict(orient="records")
        }
        json_string = json.dumps(output_data, indent=4)
        st.download_button(
            label="Download configuration as JSON",
            data=json_string,
            file_name=f"{config_name.replace(' ', '_')}_configuration.json",
            mime="application/json"
        )

    st.markdown("---")
    
    # configuration upload field
    uploaded_file = st.file_uploader("Upload a configuration file (JSON)", type=["json"])
    if uploaded_file is not None:
        try:
            file_path = os.path.join(config_folder, uploaded_file.name)
            # save the upload file in the "configurations" folder
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Configuration uploaded successfully!")
        except Exception as e:
            st.error("Error!")
    
if __name__ == "__main__":
    mechanism_configuration()