import json
from mechanism import Mechanism

def load_mechanism_from_config(file_path: str):
    # open json file from file_path
    with open(file_path, "r") as f:
        config = json.load(f)
    
    rotation_center_name = config.get("rotation_center")
    rotation_center_coords = None
    # filter out the coords of the rotation center
    for joint_conf in config["joints"]:
        if joint_conf["joint_name"] == rotation_center_name:
            rotation_center_coords = (joint_conf["x"], joint_conf["y"])
            break
    if rotation_center_coords is None:
        raise ValueError("Rotation center not found in joints configuration.")

    joints_dict = {}
    # create joints
    for joint_conf in config["joints"]: # iterate over all joints in the json
        name = joint_conf["joint_name"]
        if name == rotation_center_name:
            continue  # Skip adding the rotation center as a joint.
        x = joint_conf["x"]
        y = joint_conf["y"]
        pinned = joint_conf["pinned"]
        rotating = joint_conf["rotating_joint"]
        
        # Set the rotation center only 4 ze rotating joint
        rotate_center = rotation_center_coords if rotating else None
        # create joint object and add it to the joints_dict
        joints_dict[name] = Mechanism.Joint(x, y, pinned, rotate_center)
    
    # creat rods
    rods = []
    for rod_conf in config["rods"]:
        start_name = rod_conf["start_joint"]
        end_name = rod_conf["end_joint"]
        # error handling for not existing joints
        if start_name not in joints_dict or end_name not in joints_dict:
            raise ValueError("Rod specified joint not defined.")
        rods.append(Mechanism.Rod(joints_dict[start_name], joints_dict[end_name]))
    
    mechanism = Mechanism(list(joints_dict.values()), rods)
    # return the mechanism object
    if mechanism.config_check():
        return mechanism
    else: # basicly never reached, but just in case
        raise ValueError("Mechanism configuration is invalid.")

if __name__ == "__main__":
    from icecream import ic
    from solver import NumericSolver
    import numpy as np

    print("\n--- Test 1: Import Simple Config (1 Moving Joint) ---")

    config_file = "configurations/Viergelenkkette_configuration.json"
    mechanism = load_mechanism_from_config(config_file)

    solver = NumericSolver(mechanism)
    
    test1_angle = np.arctan(10 / 5)
    coords = solver.solve(test1_angle)
    ic(test1_angle, coords)

    test2_angle = test1_angle + np.deg2rad(10)
    coords = solver.solve(test2_angle)
    ic(test2_angle, coords)