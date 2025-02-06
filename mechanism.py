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
        self.A = self.calculate_A()
    
    def calculate_A(self):
        A = np.zeros((2 * self.m, 2 * self.n))
        for i, rod in enumerate(self.rods):
            p1 = self.joints.index(rod.start)
            p2 = self.joints.index(rod.end)
            A[2*i, 2*p1] = 1
            A[2*i, 2*p2] = -1
            A[2*i+1, 2*p1+1] = 1
            A[2*i+1, 2*p2+1] = -1
        return A
    
    def calculate_l_hat(self):
        # calculate: l^ = A * x
        x = np.array([coord for joint in self.joints for coord in (joint.x, joint.y)])
        return np.dot(self.A, x)
    
    def calculate_L(self, l_hat):
        # format l^ into L (m x 2) as described on the SWD-Slides page 15
        return l_hat.reshape(self.m, 2)
    
    def calculate_l(self, L):
        # calculate the actual lengths of the rods using the euclidean norm
        return np.linalg.norm(L, axis=1)
    
    def update_rotating_joint(self, new_theta):
        self.theta = new_theta
        r = np.linalg.norm(self.joints[self.rotating_joint_index])
        self.joints[self.rotating_joint_index] = [r * np.cos(self.theta), r * np.sin(self.theta)]
    
    def run_simulation(self):
        l_hat_old = self.calculate_l_hat()
        L_old = self.calculate_L(l_hat_old)
        l_old = self.calculate_l(L_old)
        
        return {
            "l_old": l_old
        }

if __name__ == "__main__":
    from icecream import ic
    # ------------- Testing -------------

    # Example coordinates from SWD-Slides page 13
    joints = [
        Mechanism.Joint(0, 0),
        Mechanism.Joint(10, 35),
        Mechanism.Joint(-25, 10)
    ]
    rods = [
        Mechanism.Rod(joints[0], joints[1]),
        Mechanism.Rod(joints[1], joints[2])
    ]
    rotating_joint_index = 2  # define which joint is the crank (Kurbel)
    theta = np.radians(10)  # initial rotation angle in radians

    mechanism = Mechanism(joints, rods, rotating_joint_index, theta)
    result = mechanism.run_simulation()

    # Expected result from the slides on page 16
    expected_result = [36.40054945, 43.01162634]
    #expected_result = [37, 42]

    ic(result)
    ic(expected_result)

    l_old = result["l_old"]
    assert abs(l_old[0] - expected_result[0]) < 1e-5, f"Expected {expected_result[0]}, but got {l_old[0]}"
    assert abs(l_old[1] - expected_result[1]) < 1e-5, f"Expected {expected_result[1]}, but got {l_old[1]}"

    print("All tests passed.")