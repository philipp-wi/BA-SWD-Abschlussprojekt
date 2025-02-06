import numpy as np

class Mechanism:
    class Joint:
        def __init__ (self, x: float, y: float, pinned: bool = False):
            self.x = x
            self.y = y
            self.pinned = pinned

        def __repr__(self):
            return f"Joint(X:{self.x} | Y:{self.y} | Pinned:{self.pinned})"
    
    class Rod:
        def __init__(self, start: 'Mechanism.Joint', end: 'Mechanism.Joint'):
            self.start = start
            self.end = end

        def __repr__(self):
            return f"Rod(Start:{self.start} | End:{self.end})"
        
    def __init__(self, joints: list['Mechanism.Joint'], rods: list['Mechanism.Rod'], rotating_joint_index: int, theta: float):
        self.joints = joints
        self.rods = rods
        self.rotating_joint_index = rotating_joint_index
        self.theta = theta
        self.n = len(joints)  # n = number of joints
        self.m = len(rods)    # m = number of rods
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
        self.current_angle = new_angle #update angle
        rotating_joint = self.joints[self.rotating_joint_index]

        center_of_rotation = np.array([-30, 0]) # !! Hardcoded center of rotation (should be given to function as parameter)

        # Calculate the relative position of the rotating joint to the center
        relative_position = np.array([rotating_joint.x, rotating_joint.y]) - center_of_rotation

        # Rotation matrix
        rotation_matrix = np.array([
            [np.cos(self.current_angle - self.theta), -np.sin(self.current_angle - self.theta)],
            [np.sin(self.current_angle - self.theta),  np.cos(self.current_angle - self.theta)]
        ])

        # Apply rotation
        rotated_position = rotation_matrix @ relative_position
        new_position = rotated_position + center_of_rotation

        # Update the joint with the new position
        self.joints[self.rotating_joint_index] = Mechanism.Joint(new_position[0], new_position[1], rotating_joint.pinned)

    def simulate_mechanism(self):
        joint_differences = self.calculate_joint_differences()
        joint_difference_matrix = self.calculate_joint_difference_matrix(joint_differences)
        rod_lengths = self.calculate_rod_lengths(joint_difference_matrix)
        
        return {
            "rod_lengths": rod_lengths
        }
    
    def debug_joints(self):
        for i, joint in enumerate(self.joints):
            print(f"Joint {i}: {joint}")


if __name__ == "__main__":
    from icecream import ic

    # Define joints and rods
    # Example coordinates from SWD-Slides page 13
    joints = [
        Mechanism.Joint(0, 0, True),  # Fixed joint (p0)
        Mechanism.Joint(10, 35),      # Movable joint (p1)
        Mechanism.Joint(-25, 10)      # Rotating joint (p2)
    ]
    rods = [
        Mechanism.Rod(joints[0], joints[1]),  # Rod between p0 and p1
        Mechanism.Rod(joints[1], joints[2])   # Rod between p1 and p2
    ]

    rotating_joint_index = 2  # Index of the rotating joint
    initial_angle = np.arctan(10 / 5)

    # Initialize the mechanism
    mechanism = Mechanism(joints, rods, rotating_joint_index, initial_angle)

    # Debugging: Print initial joint positions
    print("\n--- Initial Joint Positions ---")
    mechanism.debug_joints()

    # Test 1: Initial configuration
    print("\nTest with Theta = arctan(10/5)")
    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 43.01162634] # Expected result from the slides on page 16
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 1 failed!"

    # Test 2: Rotate by additional 10°
    print("\nTest with Theta + 10°")
    new_angle = initial_angle + np.radians(10)
    mechanism.update_rotating_joint_position(new_angle)

    # Debugging: Print updated joint positions
    print("\n--- Updated Joint Positions ---")
    mechanism.debug_joints()

    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 44.1005] # Expected result from the slides on page 17
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 2 failed!"

    print("\nAll tests passed!")