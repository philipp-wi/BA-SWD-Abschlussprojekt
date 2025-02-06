import numpy as np

class Mechanism:
    def __init__(self, joints, rods, rotating_joint_index, theta):
        self.joints = joints
        self.rods = rods
        self.rotating_joint_index = rotating_joint_index
        self.theta = theta
        self.n = len(joints)  # n = number of joints
        self.m = len(rods)    # m = number of rods
        self.A = self.calculate_A()
        
    def calculate_A(self):
        A = np.zeros((2 * self.m, 2 * self.n))
        for i, (p1, p2) in enumerate(self.rods):
            A[2*i, 2*p1] = 1
            A[2*i, 2*p2] = -1
            A[2*i+1, 2*p1+1] = 1
            A[2*i+1, 2*p2+1] = -1
        return A
    
    def calculate_l_hat(self):
        # calculate: l^ = A * x
        x = np.array([coord for joint in self.joints.values() for coord in joint])
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

# ------------- Testing -------------

#  used the example coordinates on page 13 (SWD-Slides) to test if the calculations work
joints = {0: [0, 0], 1: [10, 35], 2: [-25, 10]}  # define joint coordinates
rods = [(0, 1), (1, 2)]  # define rod connections
rotating_joint_index = 2  # define which joint is the crank (Kurbel)
theta = np.radians(10)  # initial rotation angle in radians


mechanism = Mechanism(joints, rods, rotating_joint_index, theta)
result = mechanism.run_simulation()
print(result)

# result: [36.40054945, 43.01162634]
# the results are correct as you can see on the slides on page 16

