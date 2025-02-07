import numpy as np

class Mechanism:
    class Joint:
        def __init__(self, x: float, y: float, pinned: bool = False, rotates_around: tuple = None):
            self.x = x
            self.y = y
            self.pinned = pinned
            self.rotate_center = rotates_around

            # store init position
            self.initial_x = x
            self.initial_y = y

            # If rotating, calculating init angle and relative position
            if self.rotate_center is not None:
                center = np.array(self.rotate_center)
                self.initial_relative = np.array([x, y]) - center
                self.initial_angle = np.arctan2(self.initial_relative[1], self.initial_relative[0])
            else:
                self.initial_relative = None
                self.initial_angle = None

        def rotate(self, absolute_angle):
            if self.rotate_center is None:
                raise ValueError("Rotation center not defined for this joint.")

            # calculate the delta angle
            delta_angle = absolute_angle - self.initial_angle

            # rotation matrix for the delta angle.
            rotation_matrix = np.array([
                [np.cos(delta_angle), -np.sin(delta_angle)],
                [np.sin(delta_angle),  np.cos(delta_angle)]
            ])

            # Rotate the stored initial relative vector.
            rotated = rotation_matrix @ self.initial_relative

            # Update the absolute position by adding the rotation center.
            self.x = rotated[0] + self.rotate_center[0]
            self.y = rotated[1] + self.rotate_center[1]

        def __repr__(self):
            return f"Joint(X:{self.x:.8f} | Y:{self.y:.8f} | Pinned:{self.pinned} | Rotates around:{self.rotate_center})"

    class Rod:
        def __init__(self, start: 'Mechanism.Joint', end: 'Mechanism.Joint'):
            self.start = start
            self.end = end

        def __repr__(self):
            start_index = joints.index(self.start)
            end_index = joints.index(self.end)
            return f"Rod(Start:{start_index} | End:{end_index})"
            #return f"Rod(Start:{self.start} | End:{self.end})"
        
    def __init__(self, joints: list['Mechanism.Joint'], rods: list['Mechanism.Rod']):
        self.joints = joints
        self.rods = rods
        self.n = len(joints)  # number of joints
        self.m = len(rods)    # number of rods
        self.A = self.calculate_connectivity_matrix()

    def calculate_connectivity_matrix(self):
        A = np.zeros((2 * self.m, 2 * self.n))
        for i, rod in enumerate(self.rods):
            p1 = self.joints.index(rod.start)
            p2 = self.joints.index(rod.end)
            A[2 * i, 2 * p1] = 1
            A[2 * i, 2 * p2] = -1
            A[2 * i + 1, 2 * p1 + 1] = 1
            A[2 * i + 1, 2 * p2 + 1] = -1
        return A
    
    def calculate_joint_differences(self):
        # calculate: l^ = A * x
        x = np.array([coord for joint in self.joints for coord in (joint.x, joint.y)])
        return np.dot(self.A, x)
    
    def calculate_joint_difference_matrix(self, l_hat):
        # format l^ into L (m x 2) as described on the SWD-Slides page 15
        return l_hat.reshape(self.m, 2)
    
    def calculate_rod_lengths(self, L):
        # calculate the actual lengths of the rods using the euclidean norm
        return np.linalg.norm(L, axis=1)
    
    def update_rotating_joint_position(self, new_angle):
        for joint in self.joints:
            if joint.rotate_center is not None:
                joint.rotate(new_angle)

    def config_check(self):
        # Check if there is exactly one rotating joint
        rotating_joints = [joint for joint in self.joints if joint.rotate_center is not None]
        if len(rotating_joints) != 1:
            raise ValueError("There must be exactly one rotating joint in the mechanism.")
        
        # Check if there is at least one pinned joint (statically fixed joint)
        pinned_joints = [joint for joint in self.joints if joint.pinned]
        if len(pinned_joints) < 1:
            raise ValueError("There must be at least one pinned joint in the mechanism.")
        
        # Check if every joint is connected to at least one rod
        unconnected_joints = [
            joint for joint in self.joints 
            if joint not in [rod.start for rod in self.rods] and joint not in [rod.end for rod in self.rods]
        ]
        if len(unconnected_joints) > 0:
            raise ValueError(f"The following joints are not connected to any rod: {unconnected_joints}")
        
        # Correct calculation of links:
        num_links = len(self.rods) + 1
        num_revolute_joints = len(self.rods)
        num_rotating_joints = len(rotating_joints)
        
        # Use the planar DoF formula for mechanisms:
        # f = 3*(L - 1) - 2*(number of revolute joints) - (number of rotating joints)
        dof = 3 * (num_links - 1) - 2 * num_revolute_joints - num_rotating_joints

        if dof != 1:
            raise ValueError(f"The mechanism must have exactly 1 degree of freedom, but it has {dof} degrees of freedom.")
        return True

    def simulate_mechanism(self):
        joint_differences = self.calculate_joint_differences()
        joint_difference_matrix = self.calculate_joint_difference_matrix(joint_differences)
        rod_lengths = self.calculate_rod_lengths(joint_difference_matrix)
        
        return {
            "rod_lengths": rod_lengths
        }
    
    def debug_print(self):
        for i, joint in enumerate(self.joints):
            print(f"Joint {i}: {joint}")
        for u, rod in enumerate(self.rods):
            print(f"Rod {u}: {rod}")


if __name__ == "__main__":
    from icecream import ic

    # Define joints and rods
    # Example coordinates from SWD-Slides page 13
    joints = [
        Mechanism.Joint(0, 0, True),  # Fixed joint (p0)
        Mechanism.Joint(10, 35),      # Movable joint (p1)
        Mechanism.Joint(-25, 10, rotates_around=(-30, 0))      # Rotating joint (p2)
    ]
    rods = [
        Mechanism.Rod(joints[0], joints[1]),  # Rod between p0 and p1
        Mechanism.Rod(joints[1], joints[2])   # Rod between p1 and p2
    ]
    
    # initialize the mechanism
    mechanism = Mechanism(joints, rods)

    # Test 0: Check configuration
    print("\n--- Test 0: Check Config ---")
    configuration_check = mechanism.config_check()
    ic(configuration_check)

    # Test 1: Rotate by arctan(10/5)
    test1_angle = np.arctan(10 / 5)
    mechanism.update_rotating_joint_position(test1_angle)
    print("\n--- Test 1: Initial Configuration (Theta = arctan(10/5) ---")
    mechanism.debug_print()
    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 43.01162634] # Expected result from the slides on page 16
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 1 failed!"

    # Test 2: Rotate by additional 10°
    test2_angle = test1_angle + np.deg2rad(10)
    mechanism.update_rotating_joint_position(test2_angle)
    print("\n--- Test 2: Updated Configuration (Theta + 10°) ---")
    mechanism.debug_print()
    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 44.1005] # Expected result from the slides on page 17
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 2 failed!"

    # Test 3: Check Config Check with invalid configuration
    print("\n--- Test 3: Check Config Check with invalid configurations ---")
    print("\n--- 3.1 no rating joints ---")
    error_counter = 0
    # Test 3.1: No rotating joint
    joints_invalid_1 = [
        Mechanism.Joint(0, 0, True),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10)
    ]
    rods_invalid_1 = [
        Mechanism.Rod(joints_invalid_1[0], joints_invalid_1[1]),
        Mechanism.Rod(joints_invalid_1[1], joints_invalid_1[2])
    ]
    mechanism_invalid_1 = Mechanism(joints_invalid_1, rods_invalid_1)
    try:
        mechanism_invalid_1.config_check()
    except ValueError as e:
        ic(e)
        error_counter += 1

    # Test 3.2: No pinned joint
    print("\n--- 3.2 no pinned joints ---")
    joints_invalid_2 = [
        Mechanism.Joint(0, 0),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10, rotates_around=(-30, 0))
    ]
    rods_invalid_2 = [
        Mechanism.Rod(joints_invalid_2[0], joints_invalid_2[1]),
        Mechanism.Rod(joints_invalid_2[1], joints_invalid_2[2])
    ]
    mechanism_invalid_2 = Mechanism(joints_invalid_2, rods_invalid_2)
    try:
        mechanism_invalid_2.config_check()
    except ValueError as e:
        ic(e)
        error_counter += 1

    # Test 3.3: Unconnected joint
    print("\n--- 3.3 unconnected joints ---")
    joints_invalid_3 = [
        Mechanism.Joint(0, 0, True),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10, rotates_around=(-30, 0)),
        Mechanism.Joint(5, 5)
    ]
    rods_invalid_3 = [
        Mechanism.Rod(joints_invalid_3[0], joints_invalid_3[1]),
        Mechanism.Rod(joints_invalid_3[1], joints_invalid_3[2])
    ]
    mechanism_invalid_3 = Mechanism(joints_invalid_3, rods_invalid_3)
    try:
        mechanism_invalid_3.config_check()
    except ValueError as e:
        ic(e)
        error_counter += 1


    # Test 3.4: Incorrect degrees of freedom
    print("\n--- 3.4 DoF Error ---")
    joints_invalid_4 = [
        Mechanism.Joint(0, 0, True),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10, rotates_around=(-30, 0)),
        Mechanism.Joint(5, 5)
    ]
    rods_invalid_4 = [
        Mechanism.Rod(joints_invalid_4[0], joints_invalid_4[1]),
        Mechanism.Rod(joints_invalid_4[1], joints_invalid_4[2]),
        Mechanism.Rod(joints_invalid_4[2], joints_invalid_4[3])
    ]
    mechanism_invalid_4 = Mechanism(joints_invalid_4, rods_invalid_4)
    try:
        mechanism_invalid_4.config_check()
    except ValueError as e:
        ic(e)
        error_counter += 1
    
    assert error_counter == 4, "Test 3 failed!"

    print("\nAll tests passed!")