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

    test1_angle = np.arctan(10 / 5)
    mechanism.update_rotating_joint_position(test1_angle)

    print("\n--- Initial Configuration (Theta = arctan(10/5) ---")
    mechanism.debug_print()

    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 43.01162634] # Expected result from the slides on page 16
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 1 failed!"

    # Test 2: Rotate by additional 10°
    test2_angle = test1_angle + np.deg2rad(10)
    mechanism.update_rotating_joint_position(test2_angle)

    # Debugging: Print updated joint positions
    print("\n--- Updated Configuration (Theta + 10°) ---")
    mechanism.debug_print()

    result = mechanism.simulate_mechanism()
    expected_rod_lengths = [36.40054945, 44.1005] # Expected result from the slides on page 17
    ic(result["rod_lengths"])
    ic(expected_rod_lengths)

    assert np.allclose(result["rod_lengths"], expected_rod_lengths, atol=1e-5), "Test 2 failed!"

    print("\nAll tests passed!")