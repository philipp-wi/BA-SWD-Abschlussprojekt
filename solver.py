import numpy as np
from scipy.optimize import least_squares
from mechanism import Mechanism

class NumericSolver:
    def __init__(self, mechanism: Mechanism):
        self.mechanism = mechanism
        # Store the reference rod lengths (assumed constant)
        joint_differences = self.mechanism.calculate_joint_differences()
        joint_difference_matrix = self.mechanism.calculate_joint_difference_matrix(joint_differences)
        self.ref_rod_lengths = self.mechanism.calculate_rod_lengths(joint_difference_matrix)
        
        # filter free joints
        self.moveable_joints = [
            i for i, joint in enumerate(self.mechanism.joints)
            if (not joint.pinned) and (joint.rotate_center is None)
        ]
    
    def calculate_differences(self, free_joint_positions):
        # update free joints with the current free_joint_positions 
        for idx, joint_index in enumerate(self.moveable_joints):
            self.mechanism.joints[joint_index].x = free_joint_positions [2 * idx]
            self.mechanism.joints[joint_index].y = free_joint_positions [2 * idx + 1]
        
        differences = []
        # For each rod, enforce: current_length - ref_length = 0.
        for i, rod in enumerate(self.mechanism.rods):
            pos_start = np.array([rod.start.x, rod.start.y])
            pos_end = np.array([rod.end.x, rod.end.y])
            current_length = np.linalg.norm(pos_start - pos_end)
            differences.append(current_length - self.ref_rod_lengths[i])
        return differences

    def solve(self, angle: float):
        # Update rotating joints of the mechanism to the desired angle.
        self.mechanism.update_rotating_joint_position(angle)

        # Build an initial guess from the current free joints positions.
        initial_guess = []
        for i in self.moveable_joints:
            joint = self.mechanism.joints[i]
            initial_guess.extend([joint.x, joint.y])
        
        # Use a least-squares optimizer to solve for free joints positions.
        result = least_squares(self.calculate_differences , initial_guess)

        # Update the mechanism with the obtained solution.
        solution = result.x
        for idx, joint_index in enumerate(self.moveable_joints):
            self.mechanism.joints[joint_index].x = solution[2 * idx]
            self.mechanism.joints[joint_index].y = solution[2 * idx + 1] # +1 to get the y coordinate
        
        # Return a dictionary mapping free joint index to its (x, y) coordinates.
        free_coords = {
            joint_index: (self.mechanism.joints[joint_index].x, self.mechanism.joints[joint_index].y)
            for joint_index in self.moveable_joints
        }
        return free_coords

if __name__ == "__main__":
    from icecream import ic

    print("\n--- Test 1: Simple Config (1 Moveable Joint) ---")
    joints = [
        Mechanism.Joint(0, 0, pinned=True),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10, rotates_around=(-30, 0))
    ]
    rods = [
        Mechanism.Rod(joints[0], joints[1]),
        Mechanism.Rod(joints[1], joints[2])
    ]
    mechanism = Mechanism(joints, rods)
    configuration_check = mechanism.config_check()
    ic(configuration_check)

    solver = NumericSolver(mechanism)
    
    test1_angle = np.arctan(10 / 5)
    coords = solver.solve(test1_angle)
    ic(test1_angle, coords)

    test2_angle = test1_angle + np.deg2rad(10)
    coords = solver.solve(test2_angle)
    ic(test2_angle, coords)
    
    print("\n--- Test 2: Advanced Config (3 Moveable Joint) ---")
    joints = [
        Mechanism.Joint(0, 0, pinned=True),
        Mechanism.Joint(10, 0),
        Mechanism.Joint(10, 10),
        Mechanism.Joint(5, 15),
        Mechanism.Joint(0, 10, rotates_around=(-5, 10))
    ]
    rods = [
        Mechanism.Rod(joints[0], joints[1]),
        Mechanism.Rod(joints[1], joints[2]),
        Mechanism.Rod(joints[2], joints[3]),
        Mechanism.Rod(joints[3], joints[4]),
        Mechanism.Rod(joints[4], joints[0])
    ]
    mechanism = Mechanism(joints, rods)

    #!! Confiuration check is not working for this case, but should...
    #configuration_check = mechanism.config_check()
    #ic(configuration_check)

    solver = NumericSolver(mechanism)
    
    test1_angle = np.arctan(10 / 5)
    coords = solver.solve(test1_angle)
    ic(test1_angle, coords)

    test2_angle = test1_angle + np.deg2rad(10)
    coords = solver.solve(test2_angle)
    ic(test2_angle, coords)